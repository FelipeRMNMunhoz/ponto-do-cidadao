# Publicação do projeto

## GitHub e execução do site

O GitHub hospeda o repositório. O GitHub Pages publica arquivos estáticos e não executa o backend Python deste projeto. Para cadastro, contato e carrinho, mantenha uma hospedagem compatível com Flask, como o PythonAnywhere.

Referências: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) e [Flask no PythonAnywhere](https://help.pythonanywhere.com/pages/Flask/).

## Preparar o envio ao GitHub

Este pacote foi exportado sem histórico Git, `.env`, bancos de dados, cadastros, uploads, ambientes virtuais e caches. Extraia-o em uma pasta nova e independente. Não o misture com o repositório antigo. O `.gitignore` também impede a inclusão acidental dos principais arquivos privados em novos commits; ele não remove dados de commits anteriores.

Uma credencial do Mercado Pago estava no código antigo. Ela não foi incluída neste pacote, mas a exportação não a revoga. Revogue-a no provedor e não envie o histórico antigo que a contém. Para um repositório novo, utilize uma cópia independente apenas com os arquivos públicos atuais, sem a pasta `.git` antiga e sem os arquivos privados. Não use `git init` na pasta atual esperando que isso apague o histórico.

Inclua código, dependências, testes, `.github/`, `.gitignore`, `.env.example`, README, SECURITY e documentação. Confirme a autorização de uso dos recursos visuais, conforme a observação no README.

Crie um repositório vazio no GitHub. Abra o terminal dentro da pasta extraída deste pacote e substitua `SEU_USUARIO` antes de executar:

```bash
git init
git branch -M main
git add .
git status
git diff --cached --stat
git commit -m "Organiza projeto acadêmico Ponto do Cidadão"
git remote add origin https://github.com/SEU_USUARIO/ponto-do-cidadao.git
git push -u origin main
```

Confira os arquivos selecionados antes do commit. Para continuar o histórico antigo, a remoção de credenciais e dados pessoais exige tratamento específico; não faça um `push --force` sem revisar esse processo.

## PythonAnywhere

Faça uma nova instalação de demonstração ou preserve um backup da aplicação atual antes de substituí-la. Não apague o banco existente.

No console Bash, dentro da pasta do projeto:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Edite `.env`, configure a chave gerada e `COOKIE_SECURE=true` para o acesso HTTPS. Em uma base nova:

```bash
python -m flask --app app:create_app init-db
python -m flask --app app:create_app seed-demo
```

Na área **Web**, configure uma aplicação Python/Flask com a mesma versão do ambiente virtual. Informe o caminho absoluto de `.venv` no campo de ambiente virtual. No arquivo WSGI disponibilizado pelo provedor, use:

```python
import sys

project_path = "/home/SEU_USUARIO/ponto-do-cidadao"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

from wsgi import application
```

Substitua o usuário e confira o caminho real. Configure `/static/` para a pasta absoluta `app/static/`. Habilite HTTPS no provedor, recarregue a aplicação e confirme que o modo debug está desativado. Não execute `app.run()` no arquivo WSGI.

Mantenha `PAYMENT_MODE=disabled` na demonstração pública. O sandbox é opcional e está descrito em ARQUITETURA.md; não habilite pagamentos reais com este fluxo incompleto.

Verifique início, campanhas, cadastro com dados fictícios, login, inclusão e alteração de quantidades, resumo e logout. O contato deve registrar a mensagem sem prometer e-mail. Confira os logs do provedor se houver erro.
