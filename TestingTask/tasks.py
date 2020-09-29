from locust import HttpLocust, TaskSet, task, ResponseError
import os

class BlurTaskSet(TaskSet):

    @task(1)
    def blur(self):
        imageFile = os.path.join(os.path.dirname(__file__),'/locust-tasks/test_image.jpg')
        with open(imageFile,'rb') as file:
            with self.client.post("/blur", files={'file':file}, verify=False) as response:
                if response.status_code != 200:
                    raise ResponseError("Request failed")
            
class BlurLocust(HttpLocust):
    task_set = BlurTaskSet