
import math


class CriptografiaSenha:
    PRIMOP = 587
    PRIMOQ = 743
    NUME = 3
    NUMD = 289875

    @staticmethod
    def __qtdBlocos(texto: str):
        qtd = 0

        for char in texto:
            qtd = qtd + 1 if char == '-' else qtd

        return qtd

    @staticmethod
    def __modReal(numero: float, classe: float):
        divisao = math.floor(numero / classe)
        return numero - (divisao * classe)

    @staticmethod
    def __elevarMod(base: float, expoente: float, nro: float):
        index = 0
        valor = 1

        while index != expoente:
            valor = valor * base
            valor = CriptografiaSenha.__modReal(valor, nro)

            index += 1

        return valor

    @staticmethod
    def codificar(codigo: str):
        preCod = ""

        for char in codigo:
            preCod = preCod + str(ord(char) + 1000)

        bloco = ""
        saida = ""

        index = 0

        while index <= (len(preCod) - 1):
            bloco = bloco + preCod[index]

            int_bloco = int(bloco)

            if int_bloco >= 50 and int_bloco < (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ) and (index == (len(preCod) - 1) or preCod[index + 1] != '0'):
                elev_mod = CriptografiaSenha.__elevarMod(
                    int_bloco, CriptografiaSenha.NUME, (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ))

                bloco = str(math.floor(elev_mod))
                saida += bloco + "-"
                index += 1
                bloco = ""
            elif int_bloco >= 50 and int_bloco < (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ) and preCod[index + 1] == '0':
                if preCod[index] == '0':
                    bloco = bloco[0:len(bloco) - 2]
                    int_bloco = int(bloco)

                    elev_mod = CriptografiaSenha.__elevarMod(
                        int_bloco, CriptografiaSenha.NUME, (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ))

                    bloco = str(math.floor(elev_mod))
                    saida += bloco + "-"
                    index -= 1
                    bloco = ""
                else:
                    bloco = bloco = bloco[0:len(bloco) - 1]
                    int_bloco = int(bloco)

                    elev_mod = CriptografiaSenha.__elevarMod(
                        int_bloco, CriptografiaSenha.NUME, (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ))

                    bloco = str(math.floor(elev_mod))
                    saida += bloco + "-"
                    bloco = ""
            elif int_bloco < 50 and index == (len(preCod) - 1):
                elev_mod = CriptografiaSenha.__elevarMod(
                    int_bloco, CriptografiaSenha.NUME, (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ))

                bloco = str(math.floor(elev_mod))
                saida += bloco + "-"
                index += 1
                bloco = ""
            elif int_bloco < 50 and preCod[index + 1] == '0':
                if (int_bloco * 10) >= (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ):
                    if preCod[index] == '0':
                        bloco = bloco[0: len(bloco) - 1]
                        int_bloco = int(bloco)

                        elev_mod = CriptografiaSenha.__elevarMod(
                            int_bloco, CriptografiaSenha.NUME, (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ))

                        bloco = str(math.floor(elev_mod))
                        saida += bloco + "-"
                        saida += "00-"
                        index += 2
                        bloco = ""
                    else:
                        bloco = bloco[0: len(bloco) - 1]
                        int_bloco = int(bloco)

                        elev_mod = CriptografiaSenha.__elevarMod(
                            int_bloco, CriptografiaSenha.NUME, (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ))

                        bloco = str(math.floor(elev_mod))
                        saida += bloco + "-"
                        bloco = ""
                else:
                    index += 1
            elif int_bloco >= (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ):
                bloco = bloco[0: len(bloco) - 1]
                int_bloco = int(bloco)

                elev_mod = CriptografiaSenha.__elevarMod(
                    int_bloco, CriptografiaSenha.NUME, (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ))

                bloco = str(math.floor(elev_mod))
                saida += bloco + "-"
                bloco = ""
            else:
                index += 1

        return saida

    @staticmethod
    def descodificar(codigo: str):
        qtdBloco = CriptografiaSenha.__qtdBlocos(codigo)

        indexI = 1
        indexJ = 0

        preCod = ""

        while indexI <= qtdBloco:
            bloco = ""

            while codigo[indexJ] != '-':
                bloco += codigo[indexJ]
                indexJ += 1

            if bloco != "00":
                int_bloco = int(bloco)
                elev_mod = CriptografiaSenha.__elevarMod(
                    int_bloco, CriptografiaSenha.NUMD, (CriptografiaSenha.PRIMOP * CriptografiaSenha.PRIMOQ))

                bloco = str(math.floor(elev_mod))
                preCod += bloco

                indexJ += 1
            else:
                preCod += "00"
                indexJ += 1

            indexI += 1

        bloco = ""
        saida = ""

        if preCod != "":
            indexI = 0

            while indexI <= len(preCod) - 1:
                if ((indexI + 1) % 4) != 0:
                    bloco += preCod[indexI]
                else:
                    bloco += preCod[indexI]
                    saida += chr(int(bloco) - 1000)
                    bloco = ""

                indexI += 1

        return saida
