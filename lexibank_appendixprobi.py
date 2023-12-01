import pathlib
import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Language, Lexeme
from pylexibank import FormSpec


#@attr.s
#class CustomLanguage(Language):
#    Location = attr.ib(default=None)
#    Remark = attr.ib(default=None)

@attr.s
class CustomLexeme(Lexeme):
    Phrase = attr.ib(default=None)
    Phrase_ID = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "appendixprobi"
    #language_class = CustomLanguage
    lexeme_class = CustomLexeme
    #form_spec = FormSpec(separators="~;,/", missing_data=[""], first_form_only=True)

    def cmd_makecldf(self, args):
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")

        # add concept
        concepts = args.writer.add_concepts(
            id_factory=lambda c: c.id.split("-")[-1] + "_" + slug(c.english),
            lookup_factory="Name",
        )
        args.log.info("added concepts")

        # add language
        for lng, gcode in [("Latin", ""), ("VulgarLatin", "")]:
            args.writer.add_language(
                    ID=lng,
                    Name=lng,
                    Glottocode=gcode)
        args.log.info("added languages")

        # read in data
        count = 1
        visited = set()
        with open(self.raw_dir / "appendix.md") as f:
            start = False
            for row in f:
                if row.strip().startswith("porphir"):
                    start = True
                if not row.strip():
                    start = False
                row = row.strip().replace(" nun ", " non ")
                if start and " non " in row:
                    if row not in visited:
                        lat, vlat = row.strip().split(" non ")
                        cidx = "{0}_{1}".format(count, slug(lat))
                        args.writer.add_concept(
                                ID=cidx,
                                Name=lat)
                        for language, value in [("Latin", lat), ("VulgarLatin",
                                                                vlat)]:
                            form = value.replace(" ", "_")
                            args.writer.add_form(
                                    Language_ID=language,
                                    Parameter_ID=cidx,
                                    Value=value,
                                    Form=form,
                                    Source="appendixprobi",
                                    Phrase=row.replace("<", "&lt;").replace(">", "&gt;"),
                                    Cognacy=count,
                                    Phrase_ID=count)
                        visited.add(row)
                        count += 1
                elif start and not " non " in row:
                    args.log.info("skipping line |{0}| ({1})".format(row.strip(), count))

