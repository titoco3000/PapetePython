import serial
import sys
import glob
import threading
import weakref

class Papete:
    def __init__(self, prioridade_porta = 0):
        self.__conexao = 'desconectado'
        self.__pe_esq = True
        self.__sensor = (0.0,0.0)
        self.prioridade_porta = prioridade_porta
        self.__main_thread = threading.current_thread()
        self.__mutex = threading.Lock()

        self.__threads_running = True
        self.__initialised = threading.Event()
        self.__t = threading.Thread(target=Papete.serial_listener,
                args=(weakref.proxy(self), ))

        self.__t.start()
        while not self.__initialised.is_set():
            # This loop is necessary to stop the main threading doing anything
            # until the exception handler in threaded_func can deal with the 
            # object being deleted.
            pass


    def serial_listener(self):
        self.__initialised.set()

        while self.__threads_running and self.__main_thread.is_alive():
            while self.__threads_running and self.__main_thread.is_alive():
                portas_disponiveis = Papete.listar_portas_disponiveis()
                #print(self.prioridade_porta, portas_disponiveis)
                if len(portas_disponiveis)>self.prioridade_porta:
                    try:
                        arduino = serial.Serial(portas_disponiveis[self.prioridade_porta], 9600,timeout=0.1)
                        break
                    except:
                        pass

            while self.__threads_running and self.__main_thread.is_alive():
                self.__conexao = 'serial'
                try:
                    data = arduino.readline().decode().strip()
                    print(data)
                    for segm in data.split('D'):
                        if len(segm) > 1:
                            pe_esq = segm[0] == 'E'[0]
                            if pe_esq:
                                segm = segm[1:]
                            numeros = segm.split('\t')
                            if len(numeros) >= 2:
                                numeros = (float(numeros[0]),float(numeros[1]))
                                with self.__mutex:
                                    self.__pe_esq = pe_esq
                                    self.__sensor = numeros
                except (UnicodeDecodeError,ValueError):
                    pass
                except serial.SerialException:
                    self.__conexao = 'desconectado'
                    break
    
    def obter_dados(self):
        with self.__mutex:
            return self.__sensor, self.__pe_esq, self.__conexao
    
    def obter_sensor(self):
        with self.__mutex:
            return self.__sensor
        
    def __str__(self):
        return f"__conexao: {self.__conexao}; lado esq: {self.__pe_esq}, valores: {self.__sensor}"

    def listar_portas_disponiveis():
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result


    def __del__(self):
        self.__threads_running = False
        self.__t.join()
