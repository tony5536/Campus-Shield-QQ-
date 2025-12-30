class Predictor:
    def __init__(self, vision_model, nlp_model):
        self.vision_model = vision_model
        self.nlp_model = nlp_model

    def predict_incident(self, image, text_input):
        vision_prediction = self.vision_model.detect(image)
        nlp_prediction = self.nlp_model.process(text_input)
        
        return {
            "vision": vision_prediction,
            "nlp": nlp_prediction
        }

    def orchestrate(self, image, text_input):
        predictions = self.predict_incident(image, text_input)
        # Additional orchestration logic can be added here
        return predictions