class Model:
    """Models defined here"""
    def __init__(self, model_name):
        self.available_models = self.get_available_models()
        
    def get_available_models(self):
        return []