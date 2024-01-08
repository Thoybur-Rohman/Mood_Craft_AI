package dev.Thoybur.MoodCraftAI;


import org.bson.types.ObjectId;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("api/v1/artwork")
public class PictureController {

    @Autowired
    private PictureService pictureService;

    @GetMapping
    public ResponseEntity<List<Pictures>> allMovies() throws IOException {
        return new ResponseEntity<List<Pictures>>(pictureService.getAllPictures(),HttpStatus.OK);
    }

    @GetMapping ("/{imdbId}")
    public ResponseEntity<Optional<Pictures>> getSingleArt(@PathVariable String imdbId) throws IOException {
        return new ResponseEntity<Optional<Pictures>>(pictureService.getPicture(imdbId),HttpStatus.OK);
    }


}
