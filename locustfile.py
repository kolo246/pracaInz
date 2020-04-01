from locust import HttpLocust, TaskSet, task
import os

class MyTaskSet(TaskSet):

    @task(3)
    def upload(self):
        imageFile = os.path.join(os.path.dirname(__file__),'test_image/DSC_0015.JPG')
        self.client.post("/upload", files={'file':open(imageFile,'rb')}, verify=False)

    @task(2)
    def blurImage(self):
        self.client.get("/blur_image")

    @task(1)
    def reset(self):
        self.client.get("/reset")

class MyLocust(HttpLocust):
    task_set = MyTaskSet
    min_wait = 5000
    max_wait = 15000