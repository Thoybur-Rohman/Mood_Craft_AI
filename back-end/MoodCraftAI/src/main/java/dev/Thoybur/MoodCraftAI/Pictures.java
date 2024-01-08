package dev.Thoybur.MoodCraftAI;


import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.DocumentReference;
import org.springframework.data.mongodb.core.mapping.Field;

import java.util.List;


@Document(collection = "Movies")
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Pictures {
        @Id
        private ObjectId id;
        private String imdbId;
        private String title;
        private String releaseDate;
        private String trailerLink;
        private String poster;
        private List<String> backdrops;
        private List<String> genres;
        @DocumentReference
        private List<Review> reviews;

}
