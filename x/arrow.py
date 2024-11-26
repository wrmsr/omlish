import pyarrow as pa
import pyarrow.parquet as pq


def _main():
    # Create an Arrow Table
    data = {
        'column1': [1, 2, 3],
        'column2': ['a', 'b', 'c']
    }
    table = pa.table(data)

    # Write to a Parquet file
    pq.write_table(table, 'example.parquet')

    # Read the Parquet file
    table = pq.read_table('example.parquet')

    # Convert the table to a Python dictionary (optional)
    data = table.to_pydict()
    print(data)

    ##

    n_legs = pa.array([2, 4, 5, 100])
    animals = pa.array(["Flamingo", "Horse", "Brittle stars", "Centipede"])
    names = ["n_legs", "animals"]
    
    # Construct a Table from a python dictionary:

    print(pa.table({"n_legs": n_legs, "animals": animals}))

    # Construct a Table from arrays:

    print(pa.table([n_legs, animals], names=names))

    # Construct a Table from arrays with metadata:

    my_metadata={"n_legs": "Number of legs per animal"}
    print(pa.table([n_legs, animals], names=names, metadata = my_metadata).schema)

    # Construct a Table from chunked arrays:

    n_legs = pa.chunked_array([[2, 2, 4], [4, 5, 100]])
    animals = pa.chunked_array([["Flamingo", "Parrot", "Dog"], ["Horse", "Brittle stars", "Centipede"]])
    table = pa.table([n_legs, animals], names=names)
    print(table)



if __name__ == '__main__':
    _main()
