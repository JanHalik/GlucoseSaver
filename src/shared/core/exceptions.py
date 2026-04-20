class GlucoseAPIException(Exception):
    def __init__(self,message):
        self.message=message

class ViewerAPIException(Exception):
    def __init__(self,message):
        self.message=message