from socket import socket, AF_INET, SOCK_RAW, IPPROTO_UDP, SOCK_DGRAM
from random import randint
from functools import reduce

def PEGAR_MEU_IPZAO():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))
    meu_ip = s.getsockname()[0]
    s.close()
    return meu_ip

MEU_IP = PEGAR_MEU_IPZAO()
PORTA_ORIGEM = 59_155

ENDERECO_SERVER = '15.228.191.109'
PORTA_SERVER = 50_000

# sempre tem 8 bytes
TAMANHO_HEADER_UDP = 8
IDENTIFICADOR = randint(1, 2**16 - 1)

def para_bytes(numero: int, num_bytes: int = 2):
    return numero.to_bytes(num_bytes, 'big')

def Requisicao():
    opcao = -1
    while opcao < 0 or opcao > 2:
        print("Qual tipo de mensagem deseja?")
        print("0. Data")
        print("1. Mensagem Motivacional (preciso)")
        print("2. Quantidade de mensagens enviadas")
        opcao = int(input("> "))

    req_tipo = 0
    match opcao:
        case 1:
            req_tipo = 1
        case 2:
            req_tipo = 2

    req_tipo = para_bytes(req_tipo, 1)
    return req_tipo

def trocar_checksum_udp(header_udp: bytearray, checksum: int):
    novo_header = header_udp.removesuffix(para_bytes(0))
    novo_header += para_bytes(checksum)
    return novo_header

def ip_para_bytes(ip: str):
    return reduce(lambda x, y: x + y, map(lambda x: para_bytes(int(x), 1), ip.split(".")), bytes())

def calcular_checksum(sequencia: bytearray):
    tam_seq = len(sequencia)

    # adiciona um byte zero no fim de sequencia
    # pra evitar catita no calculo do checksum
    if tam_seq % 2 == 1:
        sequencia += para_bytes(0, 1)

    checksum = 0

    for i in range(0, tam_seq, 2):
        primeiro_byte = sequencia[i]
        segundo_byte = sequencia[i + 1]
        byte_final = (primeiro_byte << 8) + segundo_byte
        checksum += byte_final

    checksum = ~((checksum & 65535) + (checksum >> 16)) & 65535

    return checksum

if __name__ == '__main__':
    socketCru = socket(AF_INET, SOCK_RAW, IPPROTO_UDP)

    while True:
        mensagem_envio = bytearray()

        print("Deseja fazer requisição a Empresa Catita-Ewerton-Servers?")
        opcao = input("(y/n): ")
        if opcao != 'y' and opcao != 'Y':
            #Caso o usuario não queria mais, fecha o socket
            socketCru.close()
            exit(1)

        # adiciona os 4 bits de tipo
        # vem um byte completo mas só fazemos
        # requisicao, ent n tem problema
        mensagem_envio += Requisicao()

        # Adicionando os 2 bytes do identificador
        mensagem_envio += para_bytes(IDENTIFICADOR)

        tamanho_payload = len(mensagem_envio)
        tamanho_segmento_udp = TAMANHO_HEADER_UDP + tamanho_payload

        header_udp_nosum = bytearray()
        header_udp_nosum += para_bytes(PORTA_ORIGEM)
        header_udp_nosum += para_bytes(PORTA_SERVER)
        header_udp_nosum += para_bytes(tamanho_segmento_udp)
        # checksum provisoriamente como ZERO
        header_udp_nosum += para_bytes(0)

        # criar o pseudo cabecalho IP
        pseudo_header_ip = bytearray()
        pseudo_header_ip += ip_para_bytes(MEU_IP)
        pseudo_header_ip += ip_para_bytes(ENDERECO_SERVER)
        pseudo_header_ip += para_bytes(17) # byte 0 + num protoc. trans.
        pseudo_header_ip += para_bytes(tamanho_segmento_udp)

        # calcular checksum aqui
        checksum = calcular_checksum(
            pseudo_header_ip + header_udp_nosum + mensagem_envio
        )

        # Atualiza o valor do checksum no header
        header_udp = trocar_checksum_udp(header_udp_nosum, checksum)

        ENDERECO = (ENDERECO_SERVER, PORTA_SERVER)
        mensagem = header_udp + mensagem_envio
        socketCru.sendto(mensagem, ENDERECO)
        resp_socket = socketCru.recvfrom(255)

        resp = resp_socket[0][28:]

        tipo = resp[0] & 0x0F
        match tipo:
            case 0:
                print(resp[4:-1].decode())
            case 1:
                print(resp[4:-1].decode())
            case 2:
                num = int.from_bytes(resp[4:], byteorder='big')
                print(f"Numero de resp. do serv.: {num}")
