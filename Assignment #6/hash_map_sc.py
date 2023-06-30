# Name: Michelle Mann
# OSU Email: mannm3@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: Assignment #6: Hash Map (Single Chaining)
# Due Date: June 9th, 2023 @ 11:59pm
# Description: A Hash map implementation based on a DA with single-chaining
# # -- A Hash Map is an array of items that are indexed based on a hash
# #     function. In the event of a collision, single-chaining (via a Linked
# #     Linked in each DA index) is used to house key / value pairs for
# #     specific Hash Entries.
# #
# #     This Hash Map allows for following operations: put(), empty_buckets(),
# #     table_load(), clear(), resize_table(), get(), contains_key(), remove()
# #     get_keys_and_values(), and find_mode().


from a6_include import (DynamicArray, LinkedList,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self,
                 capacity: int = 11,
                 function: callable = hash_function_1) -> None:
        """
        Initialize new HashMap that uses
        separate chaining for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(LinkedList())

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def __repr__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number and the find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        """
        Takes a key / value pair and either updates it (in the case that the
        key already exists), or adds it (in the case that it doesn't) to our
        HM.

        :param key: The key of our node.
        :param value: The value of our node.
        :return: None -- manipulates HM directly.
        """
        # Step 1) Checks the load factor of our HM at its current state. In a
        #   chained HM, load factor cannot exceed 1.
        lf = self.table_load()

        # -- If load factor is greater than 1, we need to resize.
        if lf >= 1:
            self.resize_table(self._capacity * 2)

        # Step 2) Finds the index of said key by putting it through the hash
        #   function. Assigns correct index value.
        hash_val = self._hash_function(key)
        hash_i = hash_val % self._capacity

        # Step 3) Hunts through the linked list at this index and attempts to
        #   see if key already exists. If so, updates the value associated with
        #   said key, if not adds the new key/value pair.
        ll = self._buckets[hash_i]

        if ll.length() == 0:
            ll.insert(key, value)
            self._size += 1
            return

        for ll_item in ll:
            if ll_item.key == key:
                ll_item.value = value
                return

        ll.insert(key, value)
        self._size += 1

    def empty_buckets(self) -> int:
        """
        Returns the number of empty buckets currently in our HM.

        (No Params)
        :return: The number of empty buckets (an integer)
        """
        # Stores the number of buckets available here.
        curr_buckets = self._capacity

        # Stores empty_buckets, initialized to 0.
        empty_buckets = 0

        # Iterates through the DA that holds the buckets. For each index,
        #   checks if bucket holds an empty LL. If so, increments
        #   empty_buckets. Otherwise, moves to next bucket.
        for bucket_i in range(curr_buckets):
            a_bucket = self._buckets[bucket_i]

            if a_bucket.length() == 0:
                empty_buckets += 1

        # Returns empty_buckets at end.
        return empty_buckets

    def table_load(self) -> float:
        """
        Returns the current hash table load factor. Load factor is calculated
        by dividing the number of elements stored in the table by the number
        of buckets. LF = n/m.

        This is a O(1) time complexity implementation.

        (No params)
        :return: The Load Factor of this HM
        """
        # Stores the number of elements in the table as "n".
        n = self._size

        # Stores the number of buckets in the table as "m".
        # -- m will never be 0 in this case as any time a new HM is initialized
        # -- it will default to capacity 11 or greater.
        m = self._capacity

        load_factor = n / m

        # Returns load factor
        return load_factor

    def clear(self) -> None:
        """
        Clears the contents of the hash map, but does not change the underlying
        hash table capacity.

        Implemented in O(1) time complexity.

        (No params)
        :return: None.
        """
        # Stores current capacity locally.
        curr_capacity = self._capacity

        # Iterates of each valid index in curr_capacity. For every bucket,
        #   resets all LL to empty.
        for bucket_i in range(curr_capacity):
            self._buckets[bucket_i] = LinkedList()

        # Resets size to 0 again.
        self._size = 0

    def resize_table(self, new_capacity: int) -> None:
        """
        Changes the capacity of the internal hash table. This does nothing to
        change the existing key/value pairs that already exist, but does re-
        hash these pairs into new locations and buckets.

        This does nothing if the new_capacity is less than 1 and will only
        re-size the HM to prime capacities.

        :param new_capacity: The new capacity we're attempting to re-size to.
        :return: None -- manipulates HM directly.
        """
        # Step 1) Checks that new_capacity is not less than 1. If so, returns
        #   immediately.
        if new_capacity < 1:
            return

        # Step 2) Makes sure that new_capacity is a prime number. Uses is_prime
        #   and next_prime to accomplish.
        if not self._is_prime(new_capacity):
            new_capacity = self._next_prime(new_capacity)

        # Step 2A) Sets new_da to the capacity we're looking for.
        new_da = DynamicArray()

        for item in range(new_capacity):
            new_da.append(LinkedList())

        # Step 2B) Copies self._buckets to a new location for safe keeping.
        temp_buckets = self._buckets

        # Step 3) Resets all of HM to default values with new_da as our buckets
        self._buckets = new_da
        self._capacity = new_capacity
        self._size = 0

        # Step 4) Traverses node-by-node in our original HM. For each node,
        #   hashes item via put() into our new HM object.
        for bucket_i in range(temp_buckets.length()):
            if temp_buckets[bucket_i].length() != 0:
                non_empty_bucket = temp_buckets[bucket_i]
                for a_node in non_empty_bucket:
                    self.put(a_node.key, a_node.value)

    def get(self, key: str):
        """
        Returns the value associated with a given key. If the key is not in the
        Hash Map, the method returns None.

        :param key: The key to which we want to find the value for.
        :return: A value or None. The value stored in the node identified by
        the key. Returns None if the key provided does not yet exist.
        """
        # Step 1) If HM is empty, immediately return None.
        if self._size == 0:
            return None

        # Step 2) Finds the index of said key by putting it through the hash
        #   function. Assigns correct index value.
        hash_val = self._hash_function(key)
        hash_i = hash_val % self._capacity

        # Step 3) Hunts through the linked list at this index and attempts to
        #   see if key already exists.
        ll = self._buckets[hash_i]

        # Checks through LL for whether a node with that specific key exists.
        #   If there isn't a node with that specific key, returns None.
        potential_node = ll.contains(key)

        if potential_node:
            return potential_node.value

        return None

    def contains_key(self, key: str) -> bool:
        """
        Returns true if the given key is in the HM, false if it is not. If the
        HM is empty, will return false.

        :param key: The key we're looking for.
        :return: True if exists, False if not.
        """
        # Attempts self.get(). If a value other than None occurs, return True
        if self.get(key) is not None:
            return True

        # If None is the result, return False.
        return False

    def remove(self, key: str) -> None:
        """
        Removes the given key and its associated value from the HM. If key does
        not exist, does nothing.

        :param key: The key of the node we're looking to remove.
        :return: None -- manipulates HM directly.
        """
        # Step 1) If HM is empty, immediately return.
        if self._size == 0:
            return

        # Step 2) Finds the index of said key by putting it through the hash
        #   function. Assigns correct index value.
        hash_val = self._hash_function(key)
        hash_i = hash_val % self._capacity

        # Step 3) Hunts through the linked list at this index and attempts to
        #   see if key already exists.
        ll = self._buckets[hash_i]

        # Attempts to remove specific node with key. This will default to True
        #   if successful, and False if not. If true, decrement size of HM.
        successful_remove = ll.remove(key)

        if successful_remove:
            self._size -= 1

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns a DA where each index contains a tuple of the key/value pairs
        stored in our HM.

        (No Params)
        :return: A new Dynamic Array object hosting tuples of all HM items.
        """
        # Creation of a new DA object:
        new_da = DynamicArray()

        # Iterates through each index of our DA to access each LL.
        for da_i in range(self._capacity):
            ll = self._buckets[da_i]

            # As long as the list length isn't 0, there are items in the LL.
            #   Iterates through these nodes, appending our new_list with the
            #   key, value tuple.
            if ll.length != 0:
                for ll_node in ll:
                    ll_key = ll_node.key
                    ll_value = ll_node.value
                    new_da.append((ll_key, ll_value))

        # Returns new_da at end.
        return new_da


def find_mode(da: DynamicArray) -> (DynamicArray, int):
    """
    Returns a tuple containing a DA of the most-occurring value(s) and an
    integer that represents how many times that value(s) occurred.

    This is implemented with O(n) time complexity.

    :param da: A DA object of strings.
    :return: A Tuple including a DA of the most-occurring value(s) and # of
    times it occurs.
    """
    # if you'd like to use a hash map,
    # use this instance of your Separate Chaining HashMap
    map = HashMap()
    da_length = da.length()
    new_da = DynamicArray()
    highest_freq = 0

    # For every item in the array, hash item to a spot in our new HM. Key will
    #   be the item from da, value will ultimately be the frequency it appears.
    for da_i in range(da_length):

        #   We can use map.get(key) to pull the value in the map
        potential_value = map.get(da[da_i])

        # If value is None, this is the first time we've seen this key. If not,
        #   increment this value.
        if potential_value is not None:
            potential_value += 1
        else:
            potential_value = 1

        # Put key/value back into HM with new value.
        map.put(da[da_i], potential_value)

        # Checks if potential value is newest high frequency. If so, rewrites
        #   DA to reflect this new value only. If it's equal to our previous
        #   high frequency, adds this value to our DA.
        if potential_value > highest_freq and new_da.length() != 0:
            new_da = DynamicArray()
            new_da.append(da[da_i])
            highest_freq = potential_value
        elif potential_value > highest_freq and new_da.length() == 0:
            new_da.append(da[da_i])
            highest_freq = potential_value
        elif potential_value == highest_freq:
            new_da.append(da[da_i])

    # Returns the array of highest values, and frequency in which they appear.
    return new_da, highest_freq


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":
    print("\nSelf -- wanting to know what I'm dealing with.")
    print("-------------------")
    m = HashMap(2, hash_function_1)
    print(m.get_size())
    print(m.get_capacity())
    print(m)

    print("\nTesting LF calculations")
    print("-------------------")
    m = HashMap(101)
    m._size = 3
    print(round(m.table_load(), 2))

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 1")
    print("-----------------------------")
    m = HashMap(101, hash_function_1)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 30)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key4', 40)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 2")
    print("-----------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('key' + str(i), i * 100)
        if i % 30 == 0:
            print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - table_load example 1")
    print("--------------------------")
    m = HashMap(101, hash_function_1)
    print(round(m.table_load(), 2))
    m.put('key1', 10)
    print(round(m.table_load(), 2))
    m.put('key2', 20)
    print(round(m.table_load(), 2))
    m.put('key1', 30)
    print(round(m.table_load(), 2))

    print("\nPDF - table_load example 2")
    print("--------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(50):
        m.put('key' + str(i), i * 100)
        if i % 10 == 0:
            print(round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - clear example 1")
    print("---------------------")
    m = HashMap(101, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key1', 30)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - clear example 2")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.get_size(), m.get_capacity())
    m.resize_table(100)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(23, hash_function_1)
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))

    print("\nPDF - get example 1")
    print("-------------------")
    m = HashMap(31, hash_function_1)
    print(m.get('key'))
    m.put('key1', 10)
    print(m.get('key1'))

    print("\nPDF - get example 2")
    print("-------------------")
    m = HashMap(151, hash_function_2)
    for i in range(200, 300, 7):
        m.put(str(i), i * 10)
    print(m.get_size(), m.get_capacity())
    for i in range(200, 300, 21):
        print(i, m.get(str(i)), m.get(str(i)) == i * 10)
        print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)

    print("\nPDF - contains_key example 1")
    print("----------------------------")
    m = HashMap(53, hash_function_1)
    print(m.contains_key('key1'))
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key3', 30)
    print(m.contains_key('key1'))
    print(m.contains_key('key4'))
    print(m.contains_key('key2'))
    print(m.contains_key('key3'))
    m.remove('key3')
    print(m.contains_key('key3'))

    print("\nPDF - contains_key example 2")
    print("----------------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 20)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())
    result = True
    for key in keys:
        # all inserted keys must be present
        result &= m.contains_key(str(key))
        # NOT inserted keys must be absent
        result &= not m.contains_key(str(key + 1))
    print(result)

    print("\nPDF - remove example 1")
    print("----------------------")
    m = HashMap(53, hash_function_1)
    print(m.get('key1'))
    m.put('key1', 10)
    print(m.get('key1'))
    m.remove('key1')
    print(m.get('key1'))
    m.remove('key4')

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(2)
    print(m.get_keys_and_values())

    print("\nPDF - find_mode example 1")
    print("-----------------------------")
    da = DynamicArray(["apple", "apple", "grape", "melon", "peach"])
    mode, frequency = find_mode(da)
    print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}")

    print("\nPDF - find_mode example 2")
    print("-----------------------------")
    test_cases = (
        ["Arch", "Manjaro", "Manjaro", "Mint", "Mint", "Mint", "Ubuntu", "Ubuntu", "Ubuntu"],
        ["one", "two", "three", "four", "five"],
        ["2", "4", "2", "6", "8", "4", "1", "3", "4", "5", "7", "3", "3", "2"]
    )

    for case in test_cases:
        da = DynamicArray(case)
        mode, frequency = find_mode(da)
        print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}\n")
