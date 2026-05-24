from django.db import models
from .usuarios import Funcionario
from apis.utils.upload_utils import upload_to_custom


class Categoria(models.Model):
    """Categorias de livros"""
    id_categoria = models.AutoField(primary_key=True)
    nome_categoria = models.CharField(max_length=100, unique=True, verbose_name='Nome da Categoria')
    
    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome_categoria']
    
    def __str__(self):
        return self.nome_categoria


class Livro(models.Model):
    """Livros da biblioteca"""
    id_livro = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200, verbose_name='Título')
    editora = models.CharField(max_length=150, null=True, blank=True, verbose_name='Editora')
    id_responsavel = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='livros_gerenciados',
        verbose_name='Responsável'
    )
    caminho_arquivo = models.FileField(upload_to=upload_to_custom, null=False, blank=False, verbose_name='Arquivo em PDF')
    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Categoria'
    )
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name='Data de Upload')
    img_path = models.ImageField(upload_to=upload_to_custom, null=True, blank=True, verbose_name='Capa do Livro')
    recomendado = models.BooleanField(default=False, verbose_name='Recomendado')
    
    class Meta:
        db_table = 'livro'
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        ordering = ['titulo']
    
    def __str__(self):
        return self.titulo
