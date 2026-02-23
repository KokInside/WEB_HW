const question_rate_buttons = document.querySelectorAll(".question_rate");
const answer_rate_buttons = document.querySelectorAll(".answer_rate");

// регистрация событий на кнопки лайка и дизлайка вопросов и ответов
for (let question_buttons of question_rate_buttons) {

	const question_upvote_button = question_buttons.querySelector(".upvote");
	const question_downvote_button = question_buttons.querySelector(".downvote");

	question_upvote_button.addEventListener("click", (event) => {
		const question_id = event.currentTarget.dataset["questionId"];

		questionLike(question_id);
	});

	question_downvote_button.addEventListener("click", (event) => {
		const question_id = event.currentTarget.dataset["questionId"];

		questionDislike(question_id);
	});

}

for (let answer_buttons of answer_rate_buttons) {

	const answer_upvote_button = answer_buttons.querySelector(".upvote");
	const answer_downvote_button = answer_buttons.querySelector(".downvote");

	answer_upvote_button.addEventListener("click", (event) => {
		const answer_id = event.currentTarget.dataset["answerId"];

		answerLike(answer_id);
	});

	answer_downvote_button.addEventListener("click", (event) => {
		const answer_id = event.currentTarget.dataset["answerId"];

		answerDislike(answer_id);
	});

}


function questionLike(question_id) {
	// console.log(question_id);
	// console.log("good");

	const question_like_button = document.querySelector(`#question--${question_id}--upvote`);
	const question_dislike_button = document.querySelector(`#question--${question_id}--downvote`);

	const csrf = Cookies.get("csrftoken");

	const question_likes = document.getElementById(`${question_id}--likes`);

	console.log("Запрос отправлен");

	const response = fetch(`/api/question/${question_id}/like/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	})
		.then((res) => {
			console.log("Запрос получен");
			return res.json();
		})
		.then((res) => {
			if (res.success === true) {
				// console.log(res.likes);
				question_likes.innerText = `${res.likes}`;

				if (question_like_button.classList.contains("upvoted")) {

					question_like_button.classList.remove("upvoted");
				} else {

					question_like_button.classList.add("upvoted");
				}

				question_dislike_button.classList.remove("downvoted");
			}
		})
}


function questionDislike(question_id) {
	// console.log(question_id);

	const question_like_button = document.querySelector(`#question--${question_id}--upvote`);
	const question_dislike_button = document.querySelector(`#question--${question_id}--downvote`);

	const csrf = Cookies.get("csrftoken");

	const question_likes = document.getElementById(`${question_id}--likes`);

	const response = fetch(`/api/question/${question_id}/dislike/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	})
		.then((res) => {
			return res.json();
		})
		.then((res) => {
			if (res.success === true) {
				// console.log(res.likes);
				question_likes.innerText = `${res.likes}`;

				if (question_dislike_button.classList.contains("downvoted")) {

					question_dislike_button.classList.remove("downvoted");
				} else {

					question_dislike_button.classList.add("downvoted");
				}

				question_like_button.classList.remove("upvoted");

			}
		})
}


function answerLike(answer_id) {
	// console.log(answer_id);

	const answer_like_button = document.querySelector(`#answer--${answer_id}--upvote`);
	const answer_dislike_button = document.querySelector(`#answer--${answer_id}--downvote`);

	const csrf = Cookies.get("csrftoken");

	const answer_likes = document.getElementById(`${answer_id}--likes`);

	const response = fetch(`/api/answer/${answer_id}/like/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	})
		.then((res) => {
			return res.json();
		})
		.then((res) => {
			if (res.success === true) {
				// console.log(res.likes);
				answer_likes.innerText = `${res.likes}`;

				if (answer_like_button.classList.contains("upvoted")) {

					answer_like_button.classList.remove("upvoted");
				} else {

					answer_like_button.classList.add("upvoted");
				}

				answer_dislike_button.classList.remove("downvoted");
			}
		})
}


function answerDislike(answer_id) {
	// console.log(answer_id);

	const answer_like_button = document.querySelector(`#answer--${answer_id}--upvote`);
	const answer_dislike_button = document.querySelector(`#answer--${answer_id}--downvote`);

	const csrf = Cookies.get("csrftoken");

	const answer_likes = document.getElementById(`${answer_id}--likes`);

	const response = fetch(`/api/answer/${answer_id}/dislike/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	})
		.then((res) => {
			return res.json();
		})
		.then((res) => {
			if (res.success === true) {
				// console.log(res.likes);
				answer_likes.innerText = `${res.likes}`;

				if (answer_dislike_button.classList.contains("downvoted")) {

					answer_dislike_button.classList.remove("downvoted");
				} else {

					answer_dislike_button.classList.add("downvoted");
				}

				answer_like_button.classList.remove("upvoted");
			}
		})
}