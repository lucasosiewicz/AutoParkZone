import cv2


class Scanner:
    def __init__(self, obj_model, ocr_model):
        self.obj_model = obj_model
        self.ocr_model = ocr_model
        self.car_class = 2

    def __call__(self, image_path):
        # Define a function to calculate the surface of a bounding box
        calculate_bbox_surface = lambda bbox: (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])

        # Load image and convert colorscale from BGR to RGB
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Make an inference
        results = self.obj_model(image)

        # Get the bounding box of the car
        car_boxes = results.xyxy[0]
        max_surface = 0
        
        # Iterate through all detected objects
        for bbox in car_boxes:
            # Check if detected object is a car
            if bbox[-1] == self.car_class:
                # calculate the surface of the bounding box and keep the biggest one
                surface = calculate_bbox_surface(bbox[:4])
                if surface > max_surface:
                    max_surface = surface
                    car_bbox = bbox[:4].int().tolist() 

        # If a car was detected
        if car_bbox is not None:
            # Cut the car from the image
            x1, y1, x2, y2 = car_bbox
            cropped_image = image[y1:y2, x1:x2]

            # Read the license plate
            inference = self.ocr_model.readtext(cropped_image, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', detail=0, slope_ths=0.5, width_ths=0.7, ycenter_ths=0.7)
            return inference

    
    
