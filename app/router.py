from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

faq = Route(
    name="faq",
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
    ],
    score_threshold=0.3
)

sql = Route(
    name="sql",
    utterances=[
        "I want to buy nike shoes that have 50% discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of puma running shoes?",
    ],
    score_threshold=0.3
)

smalltalk = Route(
    name="smalltalk",
    utterances=[
        "How are you?",
        "What is your name?",
        "What do you do?",
        "How is the weather today?",
    ],
    score_threshold=0.3
)

routes = [faq, sql, smalltalk]
encoder = HuggingFaceEncoder(name="sentence-transformers/all-MiniLM-L6-v2")

router = SemanticRouter(routes=routes, encoder=encoder, auto_sync="local")

if __name__ == "__main__":
    print(router("How can I track my order?").name)
    print(router("Do you have formal shoes in size 9?").name)