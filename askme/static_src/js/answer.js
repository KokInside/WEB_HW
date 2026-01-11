function sendForm(e) {
	e.preventDefault();
	// console.log("Форма перехвачена");
	// console.log(e);
	// console.log(e.currentTarget);
	// console.log(e.target);
	// console.log(e.target.action);
	const f = e.target;
	
	//console.log(f);
	
	const csrf = f.querySelector(`[name="csrfmiddlewaretoken"]`).value;
	const question_id = f.querySelector(`[name="question_id"]`).value;
	const text = document.getElementById("id_text").value;

	const text_area = document.querySelector("textarea");
	text_area.value = '';

	console.log("text = ", text);

	const data = { "question_id": question_id, "text": text };

	console.log("data = ", data);

	fetch(`/api/question/${question_id}/leave_answer/`, {
		method: "POST",
		body: JSON.stringify(data),
		headers: {
			'X-CSRFToken': csrf
		}
	}).then((res) => {
		console.log("ответ от backend:", res);
		console.log(res.json().error);
	});

}

const form = document.querySelector(".leave_answer_form");
if (form) {
	form.addEventListener("submit", sendForm);
}
