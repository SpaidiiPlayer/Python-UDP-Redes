import socket


#Função que encapsula mensagem para enviar ao servidor
#
def Requisicao(requisicao):
    opcao = -1

    while opcao<0 or opcao>2:
        print("Qual tipo de mensagem deseja?")
        print("0. Data")
        print("1. Mensagem Motivacional (preciso)")
        print("2. Quantidade de mensagens enviadas")

        opcao = int(input(""))

    if(opcao == 0):
        tipo_requisicao = 0b0000
    if(opcao == 1):
        tipo_requisicao = 0b0001
    if(opcao == 2):
        tipo_requisicao = 0b0010
    
    requisicao[0] |= tipo_requisicao

    import random
    identificador = random.randint(1, 65535)
    requisicao.extend(identificador.to_bytes(2, byteorder='big'))

    requisicao.append(0)

    return requisicao



endereco_servidor = ('15.228.191.109', 50000)                           #Endereço do servidor, que irei me conectar


Socket_Req = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           #Socket da minha máquina

menssagem_envio = bytearray()                          #variável que irei enviar ao servidor

while True:
    print("Deseja fazer requisição a Empresa Catita-Ewerton-Servers? (y)")   
    opcao = input("")
    if(opcao == 'y'):
        menssagem_envio.append(0b0000)                  
        menssagem_envio = Requisicao(menssagem_envio)       #Enviar para a funcao que preenche o mensagem de envio
    else:
        Socket_Req.close()                                  #Caso o usuario não queria mais, fecha o socket
        exit(1)

    Socket_Req.sendto(menssagem_envio, endereco_servidor)   #Envia requisicao para o servidor

    Resposta_Servidor, server = Socket_Req.recvfrom(1024)   #Recebe resposta do servidor

    if(int(Resposta_Servidor[0])==16):                       #Caso a resposta seja uma data
        for i in range(4,len(Resposta_Servidor)):
            print(chr(Resposta_Servidor[i]), end="")

    elif(int(Resposta_Servidor[0])==17):                     #Caso a resposta seja uma mensagem motivacional
        for i in range(4,(int(Resposta_Servidor[3])+3)):
            print(chr(Resposta_Servidor[i]), end="")

    elif(int(Resposta_Servidor[0])==18):                     #Caso a resposta seja o número de mensagens enviadas
        tam = len(Resposta_Servidor)-1
        Numero_Mens = int(Resposta_Servidor[tam])
        print("Mensagens enviadas: ", end='')
        print(Numero_Mens)

    print("\n")
    menssagem_envio.clear()
