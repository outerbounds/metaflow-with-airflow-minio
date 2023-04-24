from metaflow import FlowSpec, step, Parameter, environment, kubernetes

class HelloFlow(FlowSpec):
    name = Parameter('name', default='World', help='The name to say hello to')

    @step
    def start(self):
        self.name = self.name.title()
        self.next(self.end)

    @step
    def end(self):
        print('Hello, %s!' % self.name)

if __name__ == '__main__':
    HelloFlow()