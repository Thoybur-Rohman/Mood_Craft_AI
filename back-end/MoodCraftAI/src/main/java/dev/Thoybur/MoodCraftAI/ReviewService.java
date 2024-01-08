package dev.Thoybur.MoodCraftAI;


import com.mongodb.client.result.UpdateResult;
import org.bson.types.ObjectId;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.mongodb.core.query.Update;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class ReviewService {
    @Autowired
    public ReviewRepository reviewRepository;

    @Autowired
    private MongoTemplate mongoTemplate;

    public Review createReview(String reviewBody , String imdbId){
        Review review = reviewRepository.insert(new Review(reviewBody, LocalDateTime.now(), LocalDateTime.now()));

        mongoTemplate.update(Pictures.class)
                .matching(Criteria.where("imdbId").is(imdbId))
                .apply(new Update().push("reviews").value(review))
                .first();

        return review;

    }

    public void deleteReview(ObjectId reviewId) {
        // Delete the review from the review collection
        reviewRepository.deleteById(reviewId);

        // Update the Pictures document to remove the review reference
        Query query = new Query(Criteria.where("reviews").is(reviewId));
        Update update = new Update().pull("reviews", reviewId);
        mongoTemplate.updateFirst(query, update, Pictures.class);
    }




}
