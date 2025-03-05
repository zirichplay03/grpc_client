import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget, QStackedWidget,
                             QLineEdit, QFormLayout, QTabWidget, QMessageBox, QComboBox, QInputDialog)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from grpc_client import FitnessClient
from PyQt6.QtCore import QStringListModel, Qt
from PyQt6.QtWidgets import QComboBox, QListView



class ClientWindow(QMainWindow):  # Окно для клиента
    def __init__(self, full_name):
        super().__init__()

        self.full_name = full_name  # Сохраняем полное имя клиента
        self.client = FitnessClient()  # Создаем экземпляр клиента
        self.trainers = []  # Список тренеров
        self.time_slots = []  # Список времени

        self.setWindowTitle("Личный кабинет клиента")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fb;
            }
            QPushButton {
                background-color: #ff6600;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                margin: 10px 0;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #ff8533;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding-bottom: 40px;
                text-align: center;
            }
            QVBoxLayout {
                spacing: 20px;
                margin-top: 20px;
            }
            QHBoxLayout {
                spacing: 30px;
            }
        """)

        main_layout = QHBoxLayout()  # Горизонтальный layout

        # Кнопки для услуг и записи слева
        button_layout = QVBoxLayout()

        self.services_button = QPushButton("🏋️‍♂️ Услуги")
        self.services_button.clicked.connect(self.showServices)
        button_layout.addWidget(self.services_button)

        self.booking_button = QPushButton("📝 Записаться на тренировку")
        self.booking_button.clicked.connect(self.showBookingPage)
        button_layout.addWidget(self.booking_button)

        self.logout_button = QPushButton("🚪 Выйти")
        self.logout_button.clicked.connect(self.logout)
        button_layout.addWidget(self.logout_button)

        # Добавляем кнопки слева
        main_layout.addLayout(button_layout)

        # Пространство для отображения информации справа
        self.info_label = QLabel(f"Добро пожаловать, {self.full_name}! 👋")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        main_layout.addWidget(self.info_label, 1)  # Занимает 1/3 пространства

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def showBookingPage(self):
        self.info_label.setText("Выберите тренера и время для записи на тренировку 🏋️‍♂️")
        self.updateInfo()

        # Получаем список тренеров с сервера
        self.getTrainers()

        # Создаем вертикальный layout для тренера и времени
        right_layout = QVBoxLayout()

        # Создаем выпадающий список для тренеров
        self.trainer_combo = QComboBox()
        self.trainer_combo.addItems([trainer.name for trainer in self.trainers])

        # Подключаем обновление списка времени при изменении тренера
        self.trainer_combo.currentTextChanged.connect(self.getTimeSlots)

        # Создаем выпадающий список для времени
        self.time_combo = QComboBox()

        # Кнопка для записи на тренировку
        book_button = QPushButton("Записаться")
        book_button.clicked.connect(self.bookTraining)

        # Добавляем все компоненты в layout
        right_layout.addWidget(self.trainer_combo)
        right_layout.addWidget(self.time_combo)
        right_layout.addWidget(book_button)

        # Создаем горизонтальный layout для основной страницы
        main_layout = QHBoxLayout()  # Горизонтальный layout для кнопок и правой части

        # Кнопки для услуг и записи слева
        button_layout = QVBoxLayout()
        services_button = QPushButton("🏋️‍♂️ Услуги")
        services_button.clicked.connect(self.showServices)
        button_layout.addWidget(services_button)

        booking_button = QPushButton("📝 Записаться на тренировку")
        booking_button.clicked.connect(self.showBookingPage)
        button_layout.addWidget(booking_button)

        logout_button = QPushButton("🚪 Выйти")
        logout_button.clicked.connect(self.logout)
        button_layout.addWidget(logout_button)

        main_layout.addLayout(button_layout)  # Добавляем кнопки слева

        # Пространство для отображения информации справа
        self.info_label = QLabel(f"Добро пожаловать, {self.full_name}! 👋")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        main_layout.addWidget(self.info_label, 1)  # Занимает 1/3 пространства

        # Добавляем правую часть в основной layout
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def getTrainers(self):
        try:
            # Получаем список тренеров с сервера
            response = self.client.get_trainers()
            self.trainers = response.trainers
        except Exception as e:
            print(f"Ошибка при получении тренеров: {e}")
            self.trainers = []

    def getTimeSlots(self):
        try:
            # Получаем имя тренера из выпадающего списка
            trainer_name = self.trainer_combo.currentText()  # Получаем имя тренера
            response = self.client.get_schedule(trainer_name)  # Запрос расписания для тренера

            # Обновляем список времени
            self.time_slots = [schedule for schedule in response.schedule]

            # Обновляем выпадающий список для времени
            self.time_combo.clear()
            self.time_combo.addItems(self.time_slots)
        except Exception as e:
            print(f"Ошибка при получении времени: {e}")
            self.time_slots = []

    def bookTraining(self):
        try:
            trainer_name = self.trainer_combo.currentText()
            time_slot = self.time_combo.currentText()

            # Записываем клиента на тренировку
            booking_response = self.client.book_training(self.full_name, trainer_name, time_slot)

            if booking_response.success:
                QMessageBox.information(self, "Успех", "Вы успешно записаны на тренировку!")
            else:
                QMessageBox.warning(self, "Ошибка", booking_response.message)
        except Exception as e:
            print(f"Ошибка при записи на тренировку: {e}")
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка при записи на тренировку.")

    def showTrainerDialog(self, trainer_names):
        # Показываем диалог с выбором тренера
        return QInputDialog.getItem(self, "Выберите тренера", "Тренер:", trainer_names, 0, False)

    def showScheduleDialog(self, available_times):
        # Показываем диалог с выбором времени тренировки
        return QInputDialog.getItem(self, "Выберите время", "Время тренировки:", available_times, 0, False)

    def showServices(self):
        try:
            # Получаем список услуг с сервера
            response = self.client.get_services()

            # Если нет услуг
            if not response.services:
                self.info_label.setText("Услуги не доступны 😕")
                self.updateInfo()
                return

            # Если услуги есть, показываем их
            services_text = ""
            for service in response.services:
                services_text += f"✅ {service.name} - {service.price}\n👨‍🏫 Тренер: {service.trainer}\n📞 Контакт: {service.contact}\n\n"

            self.info_label.setText(services_text)
            self.updateInfo()

        except Exception as e:
            # Логируем ошибку
            print(f"Ошибка при загрузке услуг: {e}")
            self.info_label.setText("Произошла ошибка при загрузке услуг. Попробуйте позже.")
            self.updateInfo()

    def logout(self):
        self.close()  # Закрываем окно клиента

    def showButtons(self):
        self.services_button.setVisible(True)
        self.booking_button.setVisible(True)
        self.logout_button.setVisible(True)

    def updateInfo(self):
        """Обновление информации справа"""
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info_label.adjustSize()


class TrainerWindow(QMainWindow):
    def __init__(self, trainer_name):
        super().__init__()
        self.trainer_name = trainer_name
        self.client = FitnessClient()

        self.setWindowTitle("Личный кабинет тренера")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        self.setStyleSheet("""...""")
        main_layout = QVBoxLayout()

        self.clients_button = QPushButton("👥 Клиенты")
        self.clients_button.clicked.connect(self.showClients)
        main_layout.addWidget(self.clients_button)

        self.info_label = QLabel(f"Добро пожаловать, тренер {self.trainer_name}! 👋")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        main_layout.addWidget(self.info_label)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def showClients(self):
        try:
            # Получаем список клиентов тренера
            clients_info = self.client.get_trainer_clients(self.trainer_name)

            # Логируем информацию о полученных данных
            print(f"Ответ от сервера: {clients_info}")

            if not clients_info.clients:
                self.info_label.setText("У вас нет записанных клиентов.")
            else:
                clients_text = "Записанные клиенты:\n"
                for client_info in clients_info.clients:
                    # Печать информации о клиенте для отладки
                    print(f"Client Info: {client_info}")

                    # Проверка типа данных client_info
                    if hasattr(client_info, 'client_name') and hasattr(client_info, 'training_time'):
                        client_name = client_info.client_name  # Имя клиента
                        training_time = client_info.training_time  # Время тренировки

                        # Формируем текст для отображения
                        clients_text += f"Имя: {client_name}, Время: {training_time}\n"
                    else:
                        print("Неверный формат данных клиента")

                self.info_label.setText(clients_text)
        except Exception as e:
            self.info_label.setText(f"Ошибка: {e}")
            print(f"Ошибка: {e}")

    def updateInfo(self):
        """Обновление информации справа"""
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info_label.adjustSize()

    def logout(self):
        self.close()  # Закрываем окно тренера


class FitnessApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.client = FitnessClient()

        self.setWindowTitle("Run Hall - Фитнес и Спорт")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fb;
            }
            QPushButton {
                background-color: #ff6600;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                margin: 4px 0;
            }
            QPushButton:hover {
                background-color: #ff8533;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #ddd;
                padding: 6px;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #ff6600;
            }
            QLabel#footer {
                font-size: 12px;
                color: #555;
                padding: 5px;
            }
            QLabel#header {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
        """)

        # Лого и заголовок
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("img.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))

        title_label = QLabel("Добро пожаловать в Run Hall!")
        title_label.setObjectName("header")

        header_layout = QHBoxLayout()
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Меню слева
        menu_layout = QVBoxLayout()

        self.pages = QStackedWidget()

        sections = [
            "🏋️‍♂️ Услуги",
            "👤 Личный кабинет"
        ]

        for page_name in sections:
            button = QPushButton(page_name)
            button.setMinimumHeight(40)
            button.clicked.connect(lambda checked, name=page_name: self.switchPage(name))
            menu_layout.addWidget(button)

            if page_name == "👤 Личный кабинет":
                page = self.createLoginRegisterPage()
            elif page_name == "🏋️‍♂️ Услуги":
                page = self.createServicesPage()

            self.pages.addWidget(page)

        self.pages.setCurrentIndex(0)

        # Подвал
        footer_label = QLabel("📍 Контакты: +7 (495) 123-45-67 | Адрес: Москва, ул. Примерная, д. 1")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setObjectName("footer")

        # Основная компоновка
        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        content_layout.addLayout(menu_layout, 1)
        content_layout.addWidget(self.pages, 3)

        main_layout.addLayout(content_layout)
        main_layout.addWidget(footer_label)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def createLoginRegisterPage(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        login_tab = self.createLoginForm()
        register_tab = self.createRegisterForm()

        self.tabs.addTab(login_tab, "Вход")
        self.tabs.addTab(register_tab, "Регистрация")

        layout.addWidget(self.tabs)
        widget.setLayout(layout)

        return widget

    def createLoginForm(self):
        widget = QWidget()
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.login_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Логин:", self.login_input)
        form_layout.addRow("Пароль:", self.password_input)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.login)

        layout.addLayout(form_layout)
        layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)

        widget.setLayout(layout)
        return widget

    def createRegisterForm(self):
        widget = QWidget()
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.reg_login_input = QLineEdit()
        self.reg_email_input = QLineEdit()
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Логин:", self.reg_login_input)
        form_layout.addRow("Email:", self.reg_email_input)
        form_layout.addRow("Пароль:", self.reg_password_input)

        register_button = QPushButton("Зарегистрироваться")
        register_button.clicked.connect(self.register)

        layout.addLayout(form_layout)
        layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignCenter)

        widget.setLayout(layout)
        return widget

    def createServicesPage(self):
        widget = QWidget()
        layout = QVBoxLayout()

        response = self.client.get_services()

        if not response.services:
            layout.addWidget(QLabel("Нет доступных услуг 😕"))

        for service in response.services:
            label = QLabel(f"👨‍🏫 Тренер: {service.trainer}")
            label.setStyleSheet("padding: 8px; background-color: #ffffff; border: 1px solid #ddd; border-radius: 6px;")
            layout.addWidget(label)

        widget.setLayout(layout)
        return widget

    def switchPage(self, page_name):
        index = ["🏋️‍♂️ Услуги", "👤 Личный кабинет"].index(page_name)
        self.pages.setCurrentIndex(index)

    def login(self):
        try:
            # Пытаемся войти с использованием логина и пароля
            response = self.client.login(self.login_input.text(), self.password_input.text())

            if response.success:
                print(f"Login successful. Role: {response.role}, Full Name: {response.full_name}")

                # Based on role, open the respective window
                if response.role == "client":
                    self.close()  # Close the current window
                    self.client_window = ClientWindow(response.full_name)  # Pass the client name
                    self.client_window.show()

                elif response.role == "trainer":
                    self.close()  # Close the current window
                    self.client_window = TrainerWindow(response.full_name)  # Pass the client name
                    self.client_window.show()


            else:
                print(f"Login failed: {response.message}")  # Логируем ошибку при входе
                QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")

        except Exception as e:
            print(f"Error during login: {e}")  # Логируем исключение, если оно возникло
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка при попытке входа.")

    def register(self):
        response = self.client.register(self.reg_login_input.text(), self.reg_password_input.text(),
                                        self.reg_email_input.text())
        QMessageBox.information(self, "Регистрация", response.message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FitnessApp()
    window.show()
    sys.exit(app.exec())
