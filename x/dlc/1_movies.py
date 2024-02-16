import collections
import json
import typing as ta

from omlish import cached
from omlish import dataclasses as dc
import keras


"""
[
"Deadpool (film)",
{
"image": "Deadpool poster.jpg",
"name": "Deadpool",
"cinematography": "Ken Seng",
"Software Used": "Adobe Premier Pro",
"alt": "Official poster shows the titular hero Deadpool standing in front of the viewers, with hugging his hands, and donning his traditional black and red suit and mask, and the film's name, credits and billing below him.",
"distributor": "20th Century Fox",
"caption": "Theatrical release poster",
"gross": "$783.1 million",
"country": "United States",
"director": "Tim Miller",
"runtime": "108 minutes",
"editing": "Julian Clarke",
"language": "English",
"music": "Tom Holkenborg",
"budget": "$58 million"
},
[
"Tim Miller (director)",
 "Simon Kinberg",
  "Ryan Reynolds",
   "Lauren Shuler Donner",
    "Rhett Reese",
     "Paul Wernick",
      "Deadpool",
       "Fabian Nicieza",
        "Rob Liefeld",
         "Morena Baccarin",
          "Ed Skrein",
           "T.J. Miller",
            "Gina Carano",
             "Leslie Uggams", "Brianna Hildebrand", "Stefan Kapi\u010di\u0107", "Junkie XL", "Julian Clarke", "Marvel Entertainment", "Kinberg Genre", "Lauren Shuler Donner", "TSG Entertainment", "20th Century Fox", "Le Grand Rex", "Variety (magazine)", "Box Office Mojo", "superhero film", "Tim Miller (director)", "Rhett Reese", "Paul Wernick", "Marvel Comics", "Deadpool", "X-Men (film series)", "Ryan Reynolds", "Morena Baccarin", "Ed Skrein", "T.J. Miller", "Gina Carano", "Leslie Uggams", "Brianna Hildebrand", "Stefan Kapi\u010di\u0107", "antihero", "New Line Cinema", "20th Century Fox", "X-Men Origins: Wolverine", "principal photography", "Vancouver", "IMAX", "Digital Light Processing", "D-Box Technologies", "List of accolades received by Deadpool (film)", "Golden Globe Award", "Golden Globe Award for Best Motion Picture \u2013 Musical or Comedy", "Golden Globe Award for Best Actor \u2013 Motion Picture Musical or Comedy", "Producers Guild of America Award", "Critics' Choice Movie Awards", "Critics' Choice Movie Award for Best Comedy", "Critics' Choice Movie Award for Best Actor in a Comedy", "2016 in film", "#Sequels", "nonlinear narrative", "Deadpool", "special forces", "Copycat (Marvel Comics)", "Liver cancer", "Lung cancer", "Prostate cancer", "Brain tumor", "Ajax (comics)#Deadpool character", "Angel Dust (comics)", "healing factor", "rebar", "Weasel (Marvel Comics)", "Blind Al", "Colossus (comics)", "Negasonic Teenage Warhead", "X-Men", "helicarrier", "post-credits scene", "Cable (comics)", "File:Cast of Deadpool.jpg", "San Diego Comic-Con", "Ryan Reynolds", "Deadpool", "cancer", "X-Men Origins: Wolverine", "fourth wall", "Morena Baccarin", "Copycat (Marvel Comics)", "damsel in distress", "Ed Skrein", "Ajax (comics)#Deadpool character", "Weapon X", "YouTube", "Tim Miller (director)", "T.J. Miller", "Weasel (Marvel Comics)", "Simon Kinberg", "USA Today", "Gina Carano", "Angel Dust (comics)", "Leslie Uggams", "Blind Al", "Indiewire", "Brianna Hildebrand", "Negasonic Teenage Warhead", "X-Men", "Marvel Studios", "Kevin Feige", "Ego the Living Planet", "Guardians of the Galaxy Vol. 2", "Stefan Kapi\u010di\u0107", "Colossus (comics)", "Daniel Cudmore", "X2 (film)", "X-Men: The Last Stand", "X-Men: Days of Future Past", "Andre Tricoteux", "Karan Soni", "Jed Rees", "Agent Smith", "Stan Lee", "Rob Liefeld", "Isaac C. Singleton Jr.", "Bob, Agent of Hydra", "Hydra (comics)", "Nathan Fillion", "Twitter", "Simon Kinberg", "Artisan Entertainment", "Marvel Entertainment", "Deadpool", "New Line Cinema", "David S. Goyer", "Ryan Reynolds", "Shar Pei", "Cable & Deadpool", "Turnaround (filmmaking)", "X-Men Origins: Wolverine", "Lauren Shuler Donner", "Reboot (fiction)", "fourth wall", "Rhett Reese", "Paul Wernick", "Robert Rodriguez", "Tim Miller (director)", "Adam Berg (director)", "Blur Studio", "James Cameron", "David Fincher", "development hell", "Garrison Kane", "Cannonball (comics)", "Computer-generated imagery", "Hillbilly", "Wyre (comics)", "Angel Dust (comics)", "Cable (comics)", "List of directorial debuts", "Colossus (comics)", "Simon Kinberg", "The Hollywood Reporter", "T. J. Miller", "Ed Skrein", "Gina Carano", "Angel Dust (comics)", "Morena Baccarin", "Taylor Schilling", "Crystal Reed", "Rebecca Rittenhouse", "Sarah Greene (actress)", "Jessica De Gouw", "Weasel (Marvel Comics)", "Copycat (Marvel Comics)", "Brianna Hildebrand", "Negasonic Teenage Warhead", "Ajax (comics)#Deadpool character", "Leslie Uggams", "Blind Al", "Jed Rees", "Stefan Kapi\u010di\u0107", "Colossus (comics)", "Daniel Cudmore", "Twitter", "File:Deadpool, Georgia Viaduct, Vancouver, April 6 2015 - 3.jpg", "Rolling Stone", "Principal photography", "Vancouver", "stunt coordinator", "CBC News", "David Cronenberg", "Eastern Promises", "Yahoo! Movies", "Digital Domain", "Weta Digital", "Rodeo FX", "Luma Pictures", "Image Engine", "Adobe Systems", "matte paintings", "helicarrier", "Detroit", "Chicago", "File:Colossus - mocap.jpg", "Colossus (comics)", "Computer-generated imagery", "Digital Domain", "Cold-formed steel", "Hot working", "Taxicab", "Junkie XL", "ARP 2600", "Synclavier", "Oberheim Electronics#Oberheim polyphonic synthesizers", "io9", "YouTube personality", "Deadpool (video game)", "Milan Records", "Grand Rex", "IMAX", "Digital Light Processing", "D-Box Technologies", "The Hollywood Reporter", "Uzbekistan", "Central Board of Film Certification", "The Hollywood Reporter", "Hong Kong", "Singapore", "standing ovation", "The Hollywood Reporter", "Meta-joke", "Business Insider", "viral marketing", "Christmas", "Valentine's Day", "io9", "emoji", "YouTube", "Screen Junkies", "The Guardian", "Blu-ray", "2016 in film", "The Matrix Reloaded", "Forbes", "Variety (magazine)", "X-Men: Days of Future Past", "Deadline.com", "James Cameron", "George Lucas", "Star Wars: Episode III \u2013 Revenge of the Sith", "The Dark Knight Rises", "The Hollywood Reporter", "IMAX", "3D film", "Los Angeles Times", "Yahoo!", "Variety (magazine)", "Forbes (magazine)", "Presidents' Day (United States)", "Zoolander 2", "How to Be Single", "The Hollywood Reporter", "Deadline.com", "Variety (magazine)", "Guardians of the Galaxy (film)", "Captain America: The Winter Soldier", "The Hollywood Reporter", "Deadline.com", "R-rated", "The Hangover Part II", "Fifty Shades of Grey (film)", "The Hollywood Reporter", "Deadline.com", "word of mouth", "Star Wars: Episode III \u2013 Revenge of the Sith", "Forbes", "Century Theatres", "Deadline.com", "The Hollywood Reporter", "The Avengers (2012 film)", "The Hunger Games (film)", "Forbes (magazine)", "Furious 7", "Alice in Wonderland (2010 film)", "Wanted (2008 film)", "Watchmen (film)", "The Vow (2012 film)", "X-Men (film)", "X-Men: First Class", "The Wolverine (film)", "X-Men Origins: Wolverine", "Deadline.com", "Second weekend in box office performance", "Avengers: Age of Ultron", "X-Men: The Last Stand", "300 (film)", "Forbes", "The Passion of the Christ", "Forbes", "Zootopia", "London Has Fallen", "Non-Hispanic whites", "Hispanic", "African-American", "Asian Americans", "Guardians of the Galaxy (film)", "Captain America: Civil War", "Avengers: Age of Ultron", "Batman v Superman: Dawn of Justice", "Suicide Squad (film)", "The Hollywood Reporter", "Spectre (2015)", "United Kingdom and Ireland", "Chinese New Year", "Hong Kong", "Singapore", "The Mermaid (2016 film)", "Deadline.com", "Ip Man 3", "Zootopia", "Iron Man 3", "Star Wars: The Force Awakens", "Rotten Tomatoes", "Rotten Tomatoes", "Metacritic", "CinemaScore", "Peter Travers", "Rolling Stone", "Rolling Stone", "TheWrap", "Alonso Duralde", "Guardians of the Galaxy (film)", "Christy Lemire", "Richard Roeper", "Chicago Sun-Times", "Kenneth Turan", "Los Angeles Times", "Los Angeles Times", "The Hollywood Reporter", "Deadline.com", "Spider-Man", "Superhero Hype", "/Film", "Domino (comics)", "TheWrap", "Mashable", "David Leitch (filmmaker)", "Rupert Sanders", "Drew Goddard", "Mashable", "X-Force", "Hugh Jackman", "Twitter", "Variety (magazine)", "The Hollywood Reporter", "British Board of Film Classification", "Los Angeles Times", "Variety (magazine)", "MTV News", "Empire (film magazine)", "The Hollywood Reporter", "Variety (magazine)", "The Daily Dot", "Bleeding Cool", "The Hollywood Reporter", "TheWrap", "The Hollywood Reporter", "Variety (magazine)", "Entertainment Weekly", "Deadline.com", "MTV News", "Deadline.com", "Business Insider", "The Hollywood Reporter", "Twitter", "Empire (magazine)", "fxguide", "Category:20th Century Fox films", "Category:2010s action films", "Category:2010s comedy films", "Category:2010s superhero films", "Category:2016 films", "Category:American action comedy films", "Category:American black comedy films", "Category:American films", "Category:Deadpool", "Category:Directorial debut films", "Category:English-language films", "Category:Film scores by Junkie XL", "Category:Film spin-offs", "Category:Films about cancer", "Category:Films about revenge", "Category:Films directed by Tim Miller", "Category:Films set in New York", "Category:Films shot in Vancouver", "Category:Films with live action and animation", "Category:Human experimentation in fiction", "Category:IMAX films", "Category:Metafictional works", "Category:Nonlinear narrative films", "Category:Performance capture in film", "Category:Self-reflexive films", "Category:Superhero comedy films", "Category:Vigilante films", "Category:X-Men films"
],
"84%",
"6.9/10"
]
"""


@dc.dataclass(frozen=True)
class Movie:
    name: str
    dct: ta.Mapping[str, ta.Any]
    links: ta.Sequence[str]
    rat_pct: str
    rat_10: str


class MovieReqs:
    @cached.nullary
    def movies(self) -> ta.Sequence[Movie]:
        movies = []
        with open('../../../../DOsinga/deep_learning_cookbook/data/wp_movies_10k.ndjson', 'r') as f:
            for l in f.readlines():
                movies.append(Movie(*json.loads(l)))
        return movies

    @cached.nullary
    def top_links(self) -> ta.Sequence[str]:
        link_counts = collections.Counter()
        for m in self.movies():
            link_counts.update(m.links)
        return [link for link, c in link_counts.items() if c >= 3]

    @cached.nullary
    def link_to_idx(self) -> ta.Mapping[str, int]:
        return {link: idx for idx, link in enumerate(self.top_links())}

    @cached.nullary
    def movie_to_idx(self) -> ta.Mapping[str, int]:
        return {movie[0]: idx for idx, movie in enumerate(self.movies())}

    @cached.nullary
    def pairs_set(self) -> ta.AbstractSet[tuple[int, int]]:
        pairs = []
        for movie in self.movies():
            pairs.extend(
                (self.link_to_idx()[link], self.movie_to_idx()[movie[0]])
                for link in movie.links
                if link in self.link_to_idx()
            )
        pairs_set = set(pairs)
        return pairs_set

    # @cached.nullary
    # def embedding_model(self, embedding_size=50):
    #     link = keras.Input(name='link', shape=(1,))
    #     movie = keras.Input(name='movie', shape=(1,))
    #     link_embedding = keras.layers.Embedding(
    #         name='link_embedding',
    #         input_dim=len(top_links),
    #         output_dim=embedding_size,
    #     )(link)
    #     movie_embedding = keras.layers.Embedding(
    #         name='movie_embedding',
    #         input_dim=len(movie_to_idx),
    #         output_dim=embedding_size,
    #     )(movie)
    #     dot = keras.layers.Dot(
    #         name='dot_product',
    #         normalize=True,
    #         axes=2,
    #     )([link_embedding, movie_embedding])
    #     merged = keras.layers.Reshape((1,))(dot)
    #     model = keras.Model(inputs=[link, movie], outputs=[merged])
    #     model.compile(optimizer='nadam', loss='mse')
    #     return model


def _main() -> None:
    mr = MovieReqs()
    print(len(mr.pairs_set))


if __name__ == '__main__':
    _main()
