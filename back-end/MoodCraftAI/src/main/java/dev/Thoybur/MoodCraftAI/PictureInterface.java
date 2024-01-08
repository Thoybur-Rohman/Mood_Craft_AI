package dev.Thoybur.MoodCraftAI;

import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface PictureInterface extends MongoRepository<Pictures, ObjectId> {

    Optional<Pictures> findPictureByImdbId(String imdbId);
}
