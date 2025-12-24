function questionLike(question_id, csrf) {
	console.log(question_id);
	console.log("good");

	const question_likes = document.getElementById(`${question_id}--likes`);

	const response = fetch(`/api/question/${question_id}/like/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	})
		.then((res) => {
			if (res.status >= 400) {
				console.log(res.info);
			}
			return res;
		})
		.then((res) => {
			return res.json();
		})
		.then((res) => {
			question_likes.innerHTML = `${res.likes}`;
		});
}


function questionDislike(question_id, csrf) {
	console.log(question_id);

	const question_likes = document.getElementById(`${question_id}--likes`);

	const response = fetch(`/api/question/${question_id}/dislike/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	})
		.then((res) => {
			if (res.status >= 400) {
				console.log(res.info);
			}
			return res;
		})
		.then((res) => {
			return res.json();
		})
		.then((res) => {
			question_likes.innerHTML = `${res.likes}`;
		});
}


function answerLike(answer_id, csrf) {
	console.log(answer_id);

	const answer_likes = document.getElementById(`${answer_id}--likes`);

	const response = fetch(`/api/answer/${answer_id}/like/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	})
		.then((res) => {
			if (res.status >= 400) {
				console.log(res.info);
				console.log("admin")
			}
			return res;
		})
		.then((res) => {
			return res.json();
		})
		.then((res) => {
			answer_likes.innerHTML = `${res.likes}`;
		});
}


function answerDislike(answer_id, csrf) {
	console.log(answer_id);

	const answer_likes = document.getElementById(`${answer_id}--likes`);

	const response = fetch(`/api/answer/${answer_id}/dislike/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	})
		.then((res) => {
			if (res.status >= 400) {
				console.log("info " + res.info);

			}
			return res;
		})
		.then((res) => {
			return res.json();
		})
		.then((res) => {
			answer_likes.innerHTML = `${res.likes}`;
		});
}