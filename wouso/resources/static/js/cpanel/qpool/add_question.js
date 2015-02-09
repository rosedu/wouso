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
