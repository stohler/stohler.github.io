// This is your test publishable API key.
// const stripe = Stripe("pk_test_51KJ1FUCawFg96uYJ2h3F0QwdZnRxVREMnrpNPqYGLDsS7989eZkZj8ViF3sYE4G0M5AILRQZRWBk19EiClqR3cga001MLraRDr");

const stripe = Stripe("pk_test_51PT3SjP9neXzacGEJdTnbMWCYlyBebnDhsCiHseJ4x8a4pEEd5cGtliXz6Chin16XPWnYaGZPvvKSJxDivjvNgbJ00xxVvCPoZ");

const account = stripe.accounts.retrieve()
console.log("--> stripe: ", account)

throw new Error("stop here")

// The items the customer wants to buy
// const cart = {
//     "_id": "662944e6fec99f0a9f77e96b",
//     "programId": "PABPZ2E8",
//     "products": [{
//         "_id": "658b8ac3378a02d710cf2230",
//         "name": "Preparatório ENCCEJA ",
//         "sku": "5692360739",
//         "price": 8000,
//         "installments": 1,
//         "isRecurring": true
//     }],
//     "price": 8000,
//     "isEditable": true,
//     "customer": {
//         "id": "CL123456",
//         "name": "Sueli Luna Sophia Pires",
//         "email": "moneri04@moneri.com.br",
//         "document": "43040009770",
//         "phone": "96988986858"
//     },
//     "address": {
//         "zipCode": "12345-678",
//         "address": "123 Main St",
//         "number": "456",
//         "complement": "Apt 789",
//         "city": "Cityville",
//         "state": "ST"
//     },
//     "paymentType": "CREDIT_CARD",
//     "marketingData": {
//         "utmSource": "teste"
//     },
//     "description": "Pagamento cartao programa EsteticaHOme",
//     "webhook": "https://api-sandbox.moneri.com.br/v1/checkout-service/cart/65ea0f00bb7d06affd42c35d/confirm-payment/installment/1"
// };

const cart = { "clientId": "", "programId": "PABPZ2E8", "price": 7865, "products": [{ "id": "6579fc5bf3195052407d28b3", "name": "Preparatório ENCCEJA", "price": 7865, "sku": "5692360739", "quantity": 1, "installments": 1, "isRecurring": true }], "marketingData": {}, "customer": { "name": "Teste Stripe 3", "email": "testestripe3@moneri.com.br", "document": "85573870084", "phone": "21994402827", "birthDate": "1996-03-25" }, "address": { "zipCode": "22775024", "address": "Avenida Ator José Wilker", "number": "400", "complement": "", "city": "Rio de Janeiro", "state": "RJ" } };



let elements;

initialize();
checkStatus();

document
    .querySelector("#payment-form")
    .addEventListener("submit", handleSubmit);

// Fetches a payment intent and captures the client secret
async function initialize() {
    const response = await fetch("http://localhost:3000/checkout-service/cart/667b219ae0997afa28498874/create-payment-intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cart),
    });
    const { clientSecret } = await response.json();

    console.log("--> clientSecret: ", clientSecret)

    const appearance = {
        theme: 'stripe',
    };
    elements = stripe.elements({ appearance, clientSecret });

    const paymentElementOptions = {
        layout: "tabs",
        fields: {
            billingDetails: {
                address: {
                    country: 'never',
                }
            }
        }
    };

    const paymentElement = elements.create("payment", paymentElementOptions);
    paymentElement.mount("#payment-element");
}

async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
            // Make sure to change this to your payment completion page
            return_url: "file:///C:/Dev/test/stohler.github.io.git/success.html",
            return_url: "https://stohler.github.io/stripe/checkout.html",
            payment_method_data: {
                billing_details: {
                    address: {
                        country: 'BR',
                    }
                }
            }
        }
    });

    // This point will only be reached if there is an immediate error when
    // confirming the payment. Otherwise, your customer will be redirected to
    // your `return_url`. For some payment methods like iDEAL, your customer will
    // be redirected to an intermediate site first to authorize the payment, then
    // redirected to the `return_url`.
    if (error.type === "card_error" || error.type === "validation_error") {
        showMessage(error.message);
    } else {
        showMessage("An unexpected error occurred.");
    }

    setLoading(false);
}

// Fetches the payment intent status after payment submission
async function checkStatus() {
    const clientSecret = new URLSearchParams(window.location.search).get(
        "payment_intent_client_secret"
    );

    if (!clientSecret) {
        return;
    }

    const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);

    switch (paymentIntent.status) {
        case "succeeded":
            showMessage("Payment succeeded!");
            break;
        case "processing":
            showMessage("Your payment is processing.");
            break;
        case "requires_payment_method":
            showMessage("Your payment was not successful, please try again.");
            break;
        default:
            showMessage("Something went wrong.");
            break;
    }
}

// ------- UI helpers -------

function showMessage(messageText) {
    const messageContainer = document.querySelector("#payment-message");

    messageContainer.classList.remove("hidden");
    messageContainer.textContent = messageText;

    setTimeout(function() {
        messageContainer.classList.add("hidden");
        messageContainer.textContent = "";
    }, 4000);
}

// Show a spinner on payment submission
function setLoading(isLoading) {
    if (isLoading) {
        // Disable the button and show a spinner
        document.querySelector("#submit").disabled = true;
        document.querySelector("#spinner").classList.remove("hidden");
        document.querySelector("#button-text").classList.add("hidden");
    } else {
        document.querySelector("#submit").disabled = false;
        document.querySelector("#spinner").classList.add("hidden");
        document.querySelector("#button-text").classList.remove("hidden");
    }
}