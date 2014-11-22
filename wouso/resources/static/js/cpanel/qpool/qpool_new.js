var selectTagsNode = $('#select-tags');
var selectCategoryNode = $('#select-category');
var currentCategory = selectCategoryNode[0].value;

function populateTags(category) {
    $.getJSON("/api/category/" + category + "/tags", function (data) {
        selectTagsNode.empty();
        data.forEach(function (tag) {
            var name = tag.name;
            var nodeText = '<option value="' + name + '">' + name + '</option>';
            var node = $(nodeText);
            selectTagsNode.append(node);
        });
    });
}

populateTags(currentCategory);
selectCategoryNode.change(function () {
    currentCategory = selectCategoryNode[0].value;
    populateTags(currentCategory);
});


$(document).ready(function() {
	var wrapper = $('#wrapper');
	var i = $("#wrapper > div").length; // Set to the initial number of answers. We only increment i for uniqueness.
	$('#add').click(function(e) {
		e.preventDefault();
		i++;
		$('<div id="box_' + i +'" class="formfield"><div class="info-column"><a class="btn btn-sm btn-warning" id="remove"><span class="glyphicon glyphicon-minus"></span>Remove this answer</a></div><textarea name="answer_' + i +'" id="answer"></textarea><label class="mark" for="checkbox">Mark correct</label><input id="checkbox" type="checkbox" name="correct_' + i + '"/></div>').appendTo(wrapper);
	});

	$(wrapper).on('click', '#remove', function(e) {
		e.preventDefault();
		$(this).parent('div').parent('div').remove();
	});
});
