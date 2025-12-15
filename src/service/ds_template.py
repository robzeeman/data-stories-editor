template = {
    "_declaration": {
        "_attributes": {
            "version": "1.0",
            "encoding": "UTF-8"
        }
    },
    "_instruction": {"xml-model": "href=\"schema/datastory.rng\" type=\"application/xml\" schematypens=\"http://relaxng.org/ns/structure/1.0\""},
    "ds:DataStory": {
        "_attributes": {
            "xmlns:ds": "http://example.com/ds/",
            "xmlns:dct": "http://purl.org/dc/terms/",
            "xmlns:wp4": "https://github.com/CLARIAH/wp4-stories/ns#",
            "xml:lang": "en"
        },
        "ds:Metadata": {
            "dct:title": [{"_text": ""}],
            "dct:creator": [
                {"_text": ""}
            ],
            "dct:license": [{"_text": "http://creativecommons.org/licenses/by-sa/4.0/"}],
            "_comment": [
                " NOTE: any Dublin Core term https://www.dublincore.org/specifications/dublin-core/dcmi-terms/ ",
                " TODO: some more standard DS metadata elements? "
            ],
            "ds:LandingPage": [{"_text": ""}],
            "ds:Endpoint": [{"_text": ""}]
        },
        "ds:Story": {
            "ds:Block": []
        }
    }
}