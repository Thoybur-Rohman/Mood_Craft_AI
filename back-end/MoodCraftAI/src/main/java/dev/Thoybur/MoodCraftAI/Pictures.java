package dev.Thoybur.MoodCraftAI;


import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.List;


@Document(collection = "Movies")
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Pictures {
        @Id
        private ObjectId Id;

        private String imdbID;

        private String title;

        private String releaseDate;

        private String trailerLink;

        private List<String> genres;

        private List<String> backdrop;
}
