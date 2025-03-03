import grpc
import store_pb2, store_pb2_grpc


class FitnessClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = store_pb2_grpc.FitnessServiceStub(self.channel)

    def get_services(self):
        # Создаем пустой запрос
        request = store_pb2.Empty()
        # Вызываем метод на сервере для получения всех услуг
        return self.stub.GetServices(request)

    def get_trainers(self):
        request = store_pb2.Empty()
        return self.stub.GetTrainers(request)

    def get_schedule(self, trainer_name):
        request = store_pb2.TrainerScheduleRequest(trainer_name=trainer_name)
        return self.stub.GetTrainerSchedule(request)

    def get_trainer_clients(self, trainer_name):
        request = store_pb2.TrainerClientsRequest(trainer_name=trainer_name)
        return self.stub.GetTrainerClients(request)

    def book_training(self, client_name, trainer_name, time_slot):
        request = store_pb2.TrainingBookingRequest(
            client_name=client_name,
            trainer_name=trainer_name,
            training_time=time_slot
        )
        return self.stub.BookTraining(request)

    def login(self, login, password):
        request = store_pb2.LoginRequest(login=login, password=password)
        return self.stub.LoginUser(request)

    def register(self, login, password, email):
        request = store_pb2.RegisterRequest(login=login, password=password, email=email)
        return self.stub.RegisterUser(request)

    def get_client_name_by_id(self, client_id):
        request = store_pb2.ClientIdRequest(client_id=int(client_id))
        response = self.stub.GetClientName(request)
        return response.client_name

