package dev.Thoybur.MoodCraftAI;
import com.mongodb.client.gridfs.model.GridFSFile;
import org.bson.types.ObjectId;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.gridfs.GridFsOperations;
import org.springframework.data.mongodb.gridfs.GridFsTemplate;
import org.springframework.stereotype.Service;
import org.apache.commons.io.IOUtils;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import java.io.IOException;
import java.io.InputStream;
import java.util.Base64;
import java.util.List;


import java.util.List;
import java.util.Optional;

@Service
public class PictureService {

    @Autowired
    private PictureInterface pictureInterface;


    @Autowired
    private GridFsTemplate gridFsTemplate;

    private String getImageData(ObjectId imageId) throws IOException {
        GridFSFile gridFSFile = gridFsTemplate.findOne(new Query(Criteria.where("_id").is(imageId)));
        if (gridFSFile != null) {
            try (InputStream in = gridFsTemplate.getResource(gridFSFile).getInputStream()) {
                byte[] imageBytes = IOUtils.toByteArray(in);
                return Base64.getEncoder().encodeToString(imageBytes);
            }
        }
        return null;
    }

    public List<Pictures> getAllPictures() throws IOException {
        List<Pictures> picturesList = pictureInterface.findAll();
        for (Pictures picture : picturesList) {
            if (picture.getArt() != null) {
                ObjectId imageId = new ObjectId(picture.getArt());
                picture.setArt(getImageData(imageId));
            }
        }
        return picturesList;
    }

    public Optional<Pictures> getPicture(String imdbId) throws IOException {
        Optional<Pictures> pictureOpt = pictureInterface.findPictureByImdbId(imdbId);
        if (pictureOpt.isPresent()) {
            Pictures picture = pictureOpt.get();
            if (picture.getArt() != null) {
                ObjectId imageId = new ObjectId(picture.getArt());
                picture.setArt(getImageData(imageId));
            }
        }
        return pictureOpt;
    }




}
