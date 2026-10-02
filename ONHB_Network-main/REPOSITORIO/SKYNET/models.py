from django.db import models

class EDICAO(models.Model):

    id_edicao = models.AutoField(primary_key=True)

    num_edicao = models.IntegerField(verbose_name="Número da Edição")

    ano_edicao = models.IntegerField(verbose_name="Ano da Edição")

def __str__(self):
    return f"{self.num_edicao}ª ONHB ({self.ano_edicao})"

class FASE(models.Model):

    id_fase = models.AutoField(primary_key=True)

    num_fase = models.IntegerField(verbose_name="Número da Fase")

    tipo_fase = models.CharField(max_length=100,verbose_name="Tipo da Fase")

    id_edicao = models.ForeignKey(
        EDICAO,
        on_delete=models.CASCADE,
        related_name='fases',
        verbose_name="Edição")

def __str__(self):
    return f"{self.num_fase} - {self.id_edicao}"

class TIPO_QUESTAO(models.Model):

    id_tipo_questao = models.AutoField(primary_key=True)

    tipo_nome = models.CharField(max_length=100,verbose_name="Tipo de Questao")

def __str__(self):
    return f"{self.tipo_nome}"

class QUESTAO(models.Model):

    id_questao = models.AutoField(primary_key=True)

    num_questao = models.IntegerField(verbose_name="Número da Questão")

    enunciado = models.TextField(verbose_name="Enunciado da Questão")

    id_fase = models.ForeignKey(
        FASE,
        on_delete=models.CASCADE,
        related_name='Questoes',
        verbose_name="Fase")
    
    id_tipo_questao = models.ForeignKey(
        TIPO_QUESTAO,
        on_delete=models.CASCADE,
        related_name='Questoes',
        verbose_name="Tipo De Questao")
    
    documentos = models.ManyToManyField('DOCUMENTO', related_name='questoes')
    periodos = models.ManyToManyField('PERIODO', related_name='questoes')
    tags = models.ManyToManyField('TAG', related_name='questoes')
    anos = models.ManyToManyField('ANO_HISTORICO', related_name='questoes')

def __str__(self):
    return f"{self.num_questao} - {self.enunciado}"

class ITEM(models.Model):

    id_item = models.AutoField(primary_key=True)

    pontuacao = models.IntegerField(verbose_name="Pontuação do Item")

    identificador = models.CharField(verbose_name="Identificador")

    texto = models.TextField(verbose_name="Enunciado do Item")

    id_questao = models.ForeignKey(
        QUESTAO,
        on_delete=models.CASCADE,
        related_name='Tipos',
        verbose_name="Questoes")

def __str__(self):
    return f"{self.pontuacao} - {self.identificador} - {self.texto}"

class DOCUMENTO(models.Model):

    id_documento = models.AutoField(primary_key=True)

    tipo_documento = models.CharField(max_length=100,verbose_name="Tipo de Documento")

    nome_documento = models.CharField(max_length=100,verbose_name="Nome do Documento")

def __str__(self):
    return f"{self.tipo_documento} - {self.nome_documento}"

class PERIODO(models.Model):

    id_periodo = models.AutoField(primary_key=True)

    periodo_nome = models.CharField(max_length=100,verbose_name="Nome do Periodo")

    seculo = models.CharField(max_length=100,verbose_name="Seculo")

def __str__(self):
    return f"{self.seculo} - {self.periodo_nome}"

class TAG(models.Model):

    id_tag = models.AutoField(primary_key=True)

    tag_nome = models.CharField(max_length=100,verbose_name="Nome da Tag")

def __str__(self):
    return f"{self.tag_nome}"

class ANO_HISTORICO(models.Model):

    id_ano = models.AutoField(primary_key=True)

    ano = models.IntegerField(verbose_name="Ano")

def __str__(self):
    return f"{self.ano}"