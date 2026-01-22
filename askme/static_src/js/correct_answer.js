function correct(question_id, answer_id) {

	const csrf = Cookies.get("csrftoken");

	fetch(`/api/${question_id}/${answer_id}/correct/`, {
		method: "POST",
		headers: {
			'X-CSRFToken': csrf
		}
	}).then((res) => {
		if (res.status >= 400) {
			// console.log("something wrong: " + res.json.info);
		}
		return res;
	}).then((res) => {
		return res.json();
	}).then((res) => {
		const currentCorrect = res.current_correct;

		const answers_to_uncorrect = res.answers_to_uncorrect

		answers_to_uncorrect.forEach((answerID) => {
			const element = document.getElementById(`${answerID}--correct`);
			element.hidden = true;
		});

		if (currentCorrect) {
			const answerCorrect = document.getElementById(`${answer_id}--correct`);
			answerCorrect.hidden = true;			
		} else {
			const answerCorrect = document.getElementById(`${answer_id}--correct`);
			answerCorrect.hidden = false;
		}
	})
}