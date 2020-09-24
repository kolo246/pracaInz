from locust import HttpLocust, TaskSet, task
import os

class BlurTaskSet(TaskSet):

    @task(1)
    def blur(self):
        imageFile = os.path.join(os.path.dirname(__file__),'/locust-tasks/test_image.jpg')
        self.client.post("/blur", files={'file':open(imageFile,'rb')}, verify=False)
            
class BlurLocust(HttpLocust):
    task_set = BlurTaskSet