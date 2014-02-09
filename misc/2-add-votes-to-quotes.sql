-- Create the voters table
CREATE TABLE voter(
    id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Create the votes table
CREATE TABLE vote(
    id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
    vote  INT NOT NULL,
    quote INT NOT NULL REFERENCES quote(rowid) ON DELETE CASCADE,
    voter INT NOT NULL REFERENCES voter(id) ON DELETE CASCADE,
    CONSTRAINT valid_vote CHECK (vote IN (-1, 1)),
    CONSTRAINT unique_quote_voter UNIQUE (quote, voter)
);
