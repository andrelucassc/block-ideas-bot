from wit import Wit

import os
from dotenv import load_dotenv

load_dotenv()
WIT_TOKEN = os.getenv('WIT_TOKEN')

client = Wit(WIT_TOKEN)

resp = client.message('Não vamos fazer isso agora')
print(str(resp))

resp = client.message('Acho que podemos começar não?')

print(str(resp))

resp = client.message('Vish')

print(str(resp))

resp = client.message('essa é uma ideia massa')

print(str(resp))
