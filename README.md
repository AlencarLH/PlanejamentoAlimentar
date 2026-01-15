Aplicação em Python que utiliza **Algoritmo Genético** para gerar planos alimentares diários personalizados, baseados na Tabela Brasileira de Composição de Alimentos (TACO).


---------------------------------------------------------------------------------------------------------------------------
-   **Metas Personalizadas** -> Calcula necessidades calóricas e de macronutrientes com base em Biometria (Peso, Altura, Idade, Gênero, Nível de Atividade).

-   **Algoritmo Genético** -> Otimiza combinações de refeições para atingir metas nutricionais mantendo a variedade.

-   **Refeições Realistas** -> Usa modelos estruturais para garantir que as refeições façam sentido (ex: "Arroz + Feijão + Carne" para o almoço, "Pão + Laticínio" para o café).

-   **Segurança** -> Filtra automaticamente itens como carnes cruas e leguminosas cruas para garantir que apenas alimentos comestíveis sejam selecionados.

-   **Variedade** -> Gera 3 opções de cardápio distintas por execução.

-   **Interface Moderna** -> Interface web interativa construída com Streamlit.
---------------------------------------------------------------------------------------------------------------------------
**Instale as dependências**:
    ```bash
    pip install pandas streamlit
    ```

---------------------------------------------------------------------------------------------------------------------------
**UI Web (modo recomendado para visualização)**
Execute o app Streamlit:
```bash
python -m streamlit run app.py
```
Isso abrirá o Localhost no navegador.

---------------------------------------------------------------------------------------------------------------------------
**Como funciona**

1. **Carregamento dos Dados** -> O app carrega ~600 itens da tabela TACO

2. **Etiquetagem** -> Alimentos recebem tags (ex: `LUNCH_CARB`, `BREAKFAST_CEREAL`) para uso correto

3. **Evolução** -> Uma população de menus evolui por 40 gerações

4. **Seleção** -> Os 3 melhores menus distintos são apresentados
