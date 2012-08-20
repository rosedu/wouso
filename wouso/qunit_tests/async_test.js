asyncTest('jQuery test', function() {
    expect(1);

    // jQuery must be present. See suite.json.
    $(function() {
        ok(true, 'jQuery loaded.');
        start();
    });
});
