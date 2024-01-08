package dev.Thoybur.MoodCraftAI;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;

@Document (collection = "reviews")
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Review {

    private ObjectId id;
    private String review;
    private LocalDateTime created;
    private LocalDateTime updated;

    public Review(String review, LocalDateTime created, LocalDateTime updated) {
        this.review = review;
        this.created = created;
        this.updated = updated;
    }
}
