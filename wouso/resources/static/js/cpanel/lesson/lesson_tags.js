var selectTagNode = $('#select-tag');
var selectCategoryNode = $('#select-category');
var currentCategory = selectCategoryNode[0].value;

function populateTags(category) {
    $.getJSON("/api/lesson_category/" + category + "/lesson_tags", function(data) {
        selectTagNode.empty();
        data.forEach(function(tag) {
            var name = tag.name;
            var nodeText = '<option value="' + name + '">' + name + '</option>';
            var node = $(nodeText);
            selectTagNode.append(node);
        });
    });
}

if (selectTagNode.text() == '')
    populateTags(currentCategory);

selectCategoryNode.change(function() {
    currentCategory = selectCategoryNode[0].value;
    populateTags(currentCategory);
});
