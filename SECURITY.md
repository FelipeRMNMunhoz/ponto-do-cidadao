# Segurança e dados

A versão revisada remove a credencial de Mercado Pago antes presente no código. **Revogue a credencial antiga** no serviço e não publique o histórico que a contém. Não envie chaves, bancos de dados, logs de usuários ou o arquivo `.env` ao GitHub.

## Proteções implementadas

- Chave de sessão obrigatória por configuração externa.
- Senhas com hash gerado pelo Werkzeug.
- Proteção CSRF global e logout via POST.
- Verificação de conta existente para acessar o carrinho.
- Limites de campos e de tamanho de requisição.
- Validação de quantidades e cálculo monetário no servidor.
- Cookies HttpOnly e SameSite; Secure configurável para HTTPS.
- Conteúdo escapado pelos templates, X-Content-Type-Options e proteção contra enquadramento. O layout original usa CDN e estilos inline; não foi aplicada uma CSP restrita a recursos locais.
- Páginas de erro sem exposição de detalhes internos ao visitante.

## Limites conhecidos

Não há controle persistente de tentativas de login, verificação de e-mail, recuperação de senha, autenticação multifator, painel administrativo, exclusão automática ou política de retenção operacional. Esses recursos precisam ser definidos antes do uso com usuários e dados reais. Testes automatizados não constituem auditoria completa de segurança nem certificação de conformidade legal.

O cookie de sessão é assinado, não criptografado. A aplicação só coloca nele identificadores, quantidades, estado de autenticação e dados de controle. Cookies Secure dependem de `COOKIE_SECURE=true` e HTTPS na hospedagem.

O pagamento está desativado por padrão. A opção sandbox usa credenciais externas e referência única, mas não foi validada com o provedor nesta revisão. Uma operação real exige consulta autenticada ao provedor, validação de notificações, persistência de pedidos e tratamento idempotente. Redirecionamentos do navegador nunca bastam para confirmar uma doação.

Se identificar uma falha, informe os responsáveis pelo projeto por um canal privado já estabelecido. Não coloque credenciais ou dados pessoais em issues públicas.

## Publicação desta cópia

Este pacote contém somente os arquivos públicos selecionados do projeto e não inclui o histórico Git antigo. Os dados acadêmicos de autoria, escola, orientadora e ano foram preservados por fazerem parte da documentação solicitada. As credenciais presentes nos testes são fictícias. A revogação da credencial antiga depende de uma ação na conta do provedor.

O Dependabot está configurado para propor atualizações semanais das dependências Python e do GitHub Actions. Revise essas propostas e os resultados dos testes antes de integrá-las. Ative os alertas de segurança e a proteção contra envio de segredos disponíveis no seu repositório.
