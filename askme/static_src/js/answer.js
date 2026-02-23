function sendForm(e) {
	e.preventDefault();
	// console.log("Форма перехвачена");
	// console.log(e);
	// console.log(e.currentTarget);
	// console.log(e.target);
	// console.log(e.target.action);
	const form = e.target;

	//console.log(form);

	const csrf = form.querySelector(`[name="csrfmiddlewaretoken"]`).value;
	const question_id = form.querySelector(`[name="question_id"]`).value;
	const text = document.getElementById("id_text").value;

	// console.log("дошло до обработчика формы");

	const field_error = form.querySelector("#id_text_error");
	const non_field_error_list = form.querySelector("#id_non_field_error");

	non_field_error_list.hidden = true;

	if (non_field_error_list.querySelector("#already_answered_error")) {
		non_field_error_list.querySelector("#already_answered_error").remove();
	}
	
	if (field_error.querySelector("#required")) {
		field_error.querySelector("#required").remove();
	}
	
	if (text === '') {

		// console.log("текст пустой");


		// if (field_error.querySelector("#required")) {
		// 	return;
		// }
		
		const error = field_error.querySelector(".field_error").cloneNode(false);
		
		error.textContent = 'This field is required.';
		error.hidden = false;
		error.setAttribute("id", "required");
		field_error.hidden = false;
		
		field_error.appendChild(error);
		
		return;
	} else {
		field_error.hidden = true;
	}

	// console.log("текст не пустой");

	const text_area = document.querySelector("textarea");
	text_area.value = '';

	// console.log("text = ", text);

	const data = { "question_id": question_id, "text": text };

	// console.log("data = ", data);
	console.log("ДОшло до сюдова");

	fetch(`/api/question/${question_id}/leave_answer/`, {
		method: "POST",
		body: JSON.stringify(data),
		headers: {
			'X-CSRFToken': csrf
		}
	})
		.then((res) => {
			// console.log("res");
			// if (res.status >= 400) {
			// 	console.log("Алло");
			// }
			return res.json();
		})
		.then((res) => {
			
			// console.log("res json ", res);
			// console.log(res.error);

			if (!res) {
				console.log("Хоть что-то сегодня выполняться ?");
				return;
			}

			if (res.success === false) {
				// console.log("success === false");

				console.log("Вопрос невалидный");

				if (res.error === 'non_field_error') {

					const non_field_error_text = res.non_field_errors[0];
					const non_field_error_code = res.error_codes[0];

					const non_field_error_template = non_field_error_list.querySelector(".non_field_error").cloneNode(true);
					
					non_field_error_template.textContent = non_field_error_text;
					non_field_error_template.setAttribute("id", non_field_error_code);
					non_field_error_template.hidden = false;
					
					// console.log(non_field_error_template);

					non_field_error_list.appendChild(non_field_error_template);

					non_field_error_list.hidden = false;
				}
			} else {
				console.log("Вопрос валидный");
			}
		})
}

const form = document.querySelector(".leave_answer_form");
if (form) {
	form.addEventListener("submit", sendForm);
}
