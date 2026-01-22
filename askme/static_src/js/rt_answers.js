async function getToken() {
	const csrf = Cookies.get("csrftoken");

	const res = await fetch(`/api/client/jwt/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	});

	if (res.ok) {
		data = await res.json();
		return data.token;
	} else {
		return "";
	}
}

//const client = new Centrifuge('ws://localhost:8033/connection/websocket', {getToken: getToken});
//const client = new Centrifuge('http://ask.kokinside:8822/connection/websocket', {getToken: getToken});
const client = new Centrifuge('ws://ask.kokinside:8822/centrifugo/connection/websocket', { getToken: getToken });

client.on('connecting', function (ctx) {
	console.log('connecting', ctx);
});

client.on('connected', function (ctx) {
	console.log('connected', ctx);

});

client.on('disconnected', function (ctx) {
	console.log('disconnected', ctx);
});

client.connect();

// подключение к каналу
const url = new URL(document.URL);

const path_params = url.pathname.split('/');
const question_id = path_params[2];

const channel_name = `question--${question_id}--answers`;

const sub = client.newSubscription(channel_name);


sub
	.on('publication', function (ctx) {
		console.log("PUBLICATION");
		// console.log(ctx.data);

		// const author_id = ctx.data.author_id;
		// const question_id = ctx.data.question_id;
		const text = ctx.data.text;
		const author_img = ctx.data.author_img;
		const answer_id = ctx.data.answer_id;
		const author_username = ctx.data.author_username;

		// console.log("made by ", author_id);
		// console.log("with img ", author_img);
		// console.log("for question id ", question_id);
		// console.log("text ", text);
		// console.log("with answer id ", answer_id);

		const answers = document.querySelector(".answers");
		const answer = document.querySelector(".hidden-answer").cloneNode(true);

		const text_conteiner = answer.querySelector(".answer__text");
		text_conteiner.innerText = text;

		const user_link = answer.querySelector(".answer_user");
		user_link.setAttribute("href", `/profile/user/${author_username}/`);

		const user_img = answer.querySelector(".user");
		user_img.setAttribute("src", author_img);

		const rating = answer.querySelector(".rating");
		rating.setAttribute("id", `${answer_id}--likes`);

		const marked_correct = answer.querySelector(".marked");
		marked_correct.setAttribute("id", `${answer_id}--correct`);

		const answer_upvote_button = answer.querySelector(".upvote");
		const answer_downvote_button = answer.querySelector(".downvote");

		answer_upvote_button.setAttribute("id", `answer--${answer_id}--upvote`);
		answer_downvote_button.setAttribute("id", `answer--${answer_id}--downvote`);

		answer_upvote_button.dataset["answerId"] = answer_id;
		answer_downvote_button.dataset["answerId"] = answer_id;

		answer_upvote_button.addEventListener("click", (event) => {

			answerLike(answer_id);
		});

		answer_downvote_button.addEventListener("click", (event) => {
			
			answerDislike(answer_id);
		});

		answers.appendChild(answer);

		answer.hidden = false;
		answer.classList.remove('hidden-answer');

	})
	.on('subscribing', function (ctx) {
		console.log(`subscribing: ${ctx.code}, ${ctx.reason}`);
	})
	.on('subscribed', function (ctx) {
		console.log('subscribed', ctx);
	})
	.on('unsubscribed', function (ctx) {
		console.log(`unsubscribed: ${ctx.code}, ${ctx.reason}`);
	})
	.subscribe();