from time import sleep
from client import Cliente
from random import randint
from threading import Thread

class Lixeira(Cliente):

    def __init__(self, latitude, longitude):
        Cliente.__init__(self, type='lixeira', topic='setor')
        self.__latitude = latitude
        self.__longitude = longitude
        self.__capacidade = 100 #m³
        self.__bloqueado = False
        self.__lixo = 0
        self.__porcentagem = 0
        self._msg['acao'] = 'iniciar'
        print('setor/caminhao/'+self._client_id)
        
    def dadosLixeira(self):
        """Informacoes da lixeira

        Returns:
            dict: informacoes da lixeira
        """
        if(self.__bloqueado == True):
            status = "Bloqueada"
        else:
            status = "Desbloqueada"

        return {
            "id": self._client_id,
            "latitude": self.__latitude, 
            "longitude": self.__longitude, 
            "status": status, 
            "qtd_lixo": self.__lixo,
            "capacidade": self.__capacidade, 
            "porcentagem": f'{self.__porcentagem:,.3f}'+'%'
        }
    
    def addLixo(self, lixo: int):
        """Adiciona lixo na lixeira até o permitido
        
        Args
            lixo: int
                quantidade de lixo adiconada
                
        Returns: 
            boolean: retorna True se conseguir adionar lixo
        """
        if(self.__capacidade >= self.__lixo + lixo): #se a capacidade de lixo nao for excedida, o lixo é adicionado
            self.__lixo += lixo
            self.__porcentagem = self.__lixo/self.__capacidade*100
            if(self.__capacidade == self.__lixo): #se a capacidade de lixo chegar ao limite, o lixo e bloqueado
                self.__bloqueado = True
            self._msg['dados'] = self.dadosLixeira()
            self._msg['acao'] = ''
            self.enviarDados()
    
    def esvaziarLixeira(self):
        """Redefine a quantidade de lixo dentro da lixeira
        """
        if(self.__bloqueado == True):
            self.__bloqueado = False
        self.__lixo = 0
        self.__porcentagem = 0

        #retorna nova informacao sobre o objeto
        self._msg['dados'] = self.dadosLixeira()
        self._msg['acao'] = ''
        self.enviarDados()
        
        print(f"Lixeira {self._client_id} ESVAZIADA")
    
    def bloquear(self):
        """Trava a porta da lixeira
        """  
        if(self.__bloqueado == False):
            self.__bloqueado = True
            self._msg['dados'] = self.dadosLixeira()
            self._msg['acao'] = ''
            self.enviarDados()
            print(f"Lixeira {self._client_id} BLOQUEADA")

    def desbloquear(self):
        """Destrava a porta da lixeira
        """
        if(self.__capacidade > self.__lixo):
            self.__bloqueado = False
            print(f"Lixeira {self._client_id} DESBLOQUEADA")
            
            #retorna nova informacao sobre o objeto
            self._msg['dados'] = self.dadosLixeira()
            self._msg['acao'] = ''
            self.enviarDados()
        
        else:
            print(f"Lixeira Cheia! Impossível desbloquear Lixeira {self._client_id}")
    
    def generateRandomData(self):
        # options = {1: 'add', 2:'bloquear', 3:'desbloquear'}
        while self.__bloqueado == False:
            sleep(2)
            option = randint(1,3)
            
            if option == 1: self.addLixo(1)
            elif option == 2: self.bloquear()
            elif option == 3: self.desbloquear()
            
            option = 0
            sleep(3)
    
    def receberDados(self):
        """Recebe a mensagem do servidor e realiza ações
        """
        while True:
            try:
                super().receberDados()
                if( "atualizar_setor" in self._msg.get('acao')):
                    id_setor = self._msg.get('acao').split(';')[1]
                    self._msg['acao'] = ''
                    print(f"\nAlocando Lixeira para o setor {id_setor}")
                    self._client_mqtt.unsubscribe(self._topic)
                    self._topic = self._topic.split('/')[0]+'/'+id_setor+'/'+self._client_id
                    #self.connect_mqtt()
                    self._client_mqtt.subscribe(self._topic)
                    print('setor/caminhao/'+self._client_id)
                    self._client_mqtt.subscribe('setor/caminhao/'+self._client_id)
                    self.enviarDados()
                elif(self._msg.get('acao') == "esvaziar"):
                    print("Esvaziando Lixeira...")
                    self.esvaziarLixeira()
                elif(self._msg.get('acao') == "bloquear"):
                    print("Bloqueando Lixeira...")
                    self.bloquear()
                elif(self._msg.get('acao') == "desbloquear"):
                    print("Desbloqueando Lixeira...")
                    self.desbloquear()
                elif(self._msg.get('acao') == "iniciar"):
                    sleep(5)
                    self._msg['dados'] = self.dadosLixeira()
                    self.enviarDadosTopic(self._client_id)
            except Exception as ex:
                print("Erro ao receber dados => ", ex)
                break



def geradorLixeiras(velocicdade_gerarLixeira: int = 5, velocidade_gerar_addLixo: int = 5)-> Lixeira:
    """Gera lixeiras com quantidades de lixo geradas de forma aleatoria

    Args:
        velocicdade_gerarLixeira (int): velocidade em segundos que a lixeira sera criada
            5 por padrao.
        velocidade_gerar_addLixo (int): velocidade em segundos que o lixo sera adicionado. 
            5 por padrao.
    """
    sleep(velocicdade_gerarLixeira)
    l = Lixeira(latitude=randint(1, 2000), longitude=randint(1, 2000))
    l.run()
    sleep(velocidade_gerar_addLixo)
    l.addLixo(randint(1, 100))
    return l

lixeira = Lixeira(1, 4)
lixeira.run()

sleep(15)

lixeira.addLixo(100)
# while True:
#     l = geradorLixeiras()
