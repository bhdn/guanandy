from PySide import QtCore

from Guanandy.Broadcast.Signals import broadcastSignal
from Guanandy.Protocol.Signals import protocolSignal
from Guanandy import Controller


class Teacher(QtCore.QObject):
    def __init__(self, name, ip, port, parent):
        super(Teacher, self).__init__(parent)
        self.__name = name
        self.__ip = ip
        self.__port = port

        # Attribute definition
        self.subscriber = None
        self.request = None
        self.studentName = None

    def connect(self, studentName):
        """
        Connect to teacher server
        """
        self.studentName = studentName
        self.subscriber = Controller.Subscriber(self.ip, self.port, studentName, parent=self)
        self.subscriber.start()

        self.request = Controller.Request(self.ip, 65533, parent=self)
        self.request.start()

        self.registerStudent()

    def stop(self):
        """
        Stop connection with teacher
        """
        # TODO: Send a student will shutdown message to teacher
        self.subscriber.stop()
        self.request.stop()

    def registerStudent(self):
        """
        Register in a classroom
        """
        self.request.registerStudent(self.studentName)

    def callAttention(self):
        """
        Send call attention message
        """
        self.request.callAttention(self.studentName)

    def __getName(self):
        return str(self.__name)

    def __getIp(self):
        return str(self.__ip)

    def __getPort(self):
        return str(self.__port)

    changed = QtCore.Signal()
    name = QtCore.Property(unicode, __getName, notify=changed)
    ip = QtCore.Property(unicode, __getIp, notify=changed)
    port = QtCore.Property(unicode, __getPort, notify=changed)


class TeacherModel(QtCore.QAbstractListModel):

    def __init__(self, parent):
        super(TeacherModel, self).__init__(parent)
        self.__teachers = []
        broadcastSignal.teacherFound.connect(self.add)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.__teachers)

    def data(self, index, role=QtCore.Qt.DisplayRole):

        # This role return teacher or classroom name
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return self.__teachers[index.row()].name

        # This role return teacher or classroom object instance
        if index.isValid() and role == 1111:
            return self.__teachers[index.row()]

        return None

    def add(self, name, ip, port):
        for t in self.__teachers:
            if t.name == name:
                return
        self.beginInsertRows(QtCore.QModelIndex(), len(self.__teachers),
                len(self.__teachers))
        teacher = Teacher(name, ip, port, self)
        self.__teachers.append(teacher)
        self.endInsertRows()
