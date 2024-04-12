document.addEventListener('DOMContentLoaded', function() {
  var curriculumListField = document.getElementById('id_curriculum_list');
  var curriculumList = curriculumListField.value.split(',');

  var container = document.createElement('div');
  container.classList.add('curriculum-input-container');

  curriculumList.forEach(function(curriculum, index) {
      var label = document.createElement('label');
      label.textContent = curriculum;

      var input = document.createElement('input');
      input.name = 'curriculum_list_input';
      input.type = 'text';
      container.appendChild(label);
      container.appendChild(input);
  });

  curriculumListField.parentNode.insertBefore(container, curriculumListField.nextSibling);
});
// document.addEventListener('DOMContentLoaded', function() {
//   var curriculumListField = document.getElementById('id_curriculum_list');
//   var curriculumList = curriculumListField.value.split(',');

//   var container = document.createElement('div');
//   container.classList.add('curriculum-input-container');

//   curriculumList.forEach(function(curriculumStack, index) {
//       var stackLabel = document.createElement('label');
//       stackLabel.textContent = curriculumStack;
//       container.appendChild(stackLabel);

//       var curriculumNames = curriculumStack.split(';');
//       curriculumNames.forEach(function(curriculumName) {
//           var label = document.createElement('label');
//           label.textContent = curriculumName;

//           var input = document.createElement('input');
//           input.name = 'curriculum_list_input';
//           input.type = 'text';
//           input.dataset.curriculumStack = curriculumStack;
//           input.dataset.curriculumName = curriculumName;

//           container.appendChild(label);
//           container.appendChild(input);
//       });
//   });

//   curriculumListField.parentNode.insertBefore(container, curriculumListField.nextSibling);
// });
