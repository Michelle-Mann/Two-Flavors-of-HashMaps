# Name: Michelle Mann
# OSU Email: mannm3@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: Assignment #6: Hash Map (Open Addressing)
# Due Date: June 9th, 2023 @ 11:59pm
# Description: A Hash map implementation based on a DA with quadratic probing
# # -- A Hash Map is an array of items that are indexed based on a hash
# #     function. In the event of a collision, quadratic probing is used to
# #     to find alternative index values for specific Hash Entries.
# #
# #     This Hash Map allows for following operations: put(), empty_buckets(),
# #     table_load(), clear(), resize_table(), get(), contains_key(), remove()
# #     get_keys_and_values(), and __iter__(), __next__()

from typing import Tuple, Any

from a6_include import (DynamicArray, DynamicArrayException, HashEntry,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

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
        Increment from given number to find the closest prime number
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

    def quad_prob(self, key, job) -> int:
        """
        Returns a viable index of a non-occupied slot in our DA. Uses the
        index provided to assess where the Hash Entry should go based on our
        hash function as a starting place. If key is used, hunts for key.
        """
        # Initializes start_j as 1. Increments this each loop.
        start_j = 0

        # The new index, will be with quadratic probing of our j-value.
        new_i = (self._hash_function(key) + start_j ** 2) % self._capacity

        # Temporarily stores our buckets, our function and our capacity locally
        buckets = self._buckets
        hash_fun = self._hash_function
        cap = self._capacity

        # For put() specifically, we will stop looping for tombstones OR None
        #   OR if the key we're dealing with already exists.
        if job == 'put':
            while buckets[new_i] and not buckets[new_i].is_tombstone \
                    and buckets[new_i].key != key:
                start_j += 1
                new_i = (hash_fun(key) + start_j ** 2) % cap

            return new_i

        # For get() or remove(), we'll skip over tombstones until we hit None.
        while buckets[new_i] and buckets[new_i].key != key:
            start_j += 1
            new_i = (hash_fun(key) + start_j ** 2) % cap

        return new_i

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
        #   open-address HM, load factor cannot exceed 0.5.
        lf = self.table_load()

        # -- If load factor is greater than 0.5, we need to resize.
        if lf >= 0.5:
            self.resize_table(self._capacity * 2)

        # Step 2) Finds the index of said key by putting it through the hash
        #   function. Assigns correct index value and determines if this is a
        #   node rewrite.
        hash_i = self.quad_prob(key, 'put')

        # If this is not a node rewrite, we increment size. If index holds
        #   None or a tombstone, we won't have a re-write.
        if not self._buckets[hash_i] or \
                self._buckets[hash_i].is_tombstone:
            self._size += 1

        self._buckets[hash_i] = HashEntry(key, value)

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
        # -- it will default to capacity 1 or greater.
        m = self._capacity

        load_factor = n / m

        # Returns load factor
        return load_factor

    def empty_buckets(self) -> int:
        """
        Returns the number of empty buckets currently in our HM.

        (No Params)
        :return: The number of empty buckets (an integer)
        """
        # Stores the number of buckets available here.
        curr_buckets = self._capacity

        # Stores the number of items in the HM.
        curr_size = self._size

        # Returns the number of buckets minus the number of HM items.
        return curr_buckets - curr_size

    def resize_table(self, new_capacity: int) -> None:
        """
        Changes the capacity of the internal hash table. This does nothing to
        change the existing key/value pairs that already exist, but does re-
        hash these pairs into new locations and buckets.

        This does nothing if the new_capacity is less than it's size and will
        only re-size the HM to prime capacities.

        :param new_capacity: The new capacity we're attempting to re-size to.
        :return: None -- manipulates HM directly.
        """
        # Step 1) Checks that new_capacity is not less than 1. If so, returns
        #   immediately.
        if new_capacity < self._size:
            return

        # Step 2) Makes sure that new_capacity is a prime number. Uses is_prime
        #   and next_prime to accomplish.
        if not self._is_prime(new_capacity):
            new_capacity = self._next_prime(new_capacity)

        # Step 2A) Sets new_da to the capacity we're looking for.
        new_da = DynamicArray()

        for item in range(new_capacity):
            new_da.append(None)

        # Step 2B) Copies self._buckets to a new location for safe keeping.
        temp_buckets = self._buckets

        # Step 3) Resets all of HM to default values with new_da as our buckets
        self._buckets = new_da
        self._capacity = new_capacity
        self._size = 0

        # Step 3) Traverses node-by-node in our original HM. For each node,
        #   hashes item via put() into our new HM object.

        for bucket_i in range(temp_buckets.length()):
            if temp_buckets[bucket_i] and \
                    not temp_buckets[bucket_i].is_tombstone:
                non_empty_bucket = temp_buckets[bucket_i]
                self.put(non_empty_bucket.key, non_empty_bucket.value)

    def get(self, key: str) -> object:
        """
        Returns the value associated with the given key. If the key is not in
        our HM, returns None.

        :param key: The key we are ultimately looking for.
        :return: The value associated with said key.
        """
        # Step 1) If HM is empty, immediately return None.
        if self._size == 0:
            return None

        # Step 2) Finds the index of said key by putting it through the hash
        #   function. Assigns correct index value.
        hash_i = self.quad_prob(key, 'get')

        # Step 3) Hunts through our buckets for this particular key, attempting
        #   quadratic probing if the initial hash_i value does not exist.
        # -- In this case, we've found the theoretical location of this key.
        #   Check it. If it is None, the key doesn't exist, and if the key at
        #   this index is not the key we're looking for, it probably DNE.
        if self._buckets[hash_i] is None or self._buckets[hash_i].key != key \
                or self._buckets[hash_i].is_tombstone:
            return None

        # If it does exist, return its value.
        return self._buckets[hash_i].value

    def contains_key(self, key: str) -> bool:
        """
        Returns true if the given key is a part of our HM, and False if it is
        not. If called on an empty HM, will return False.
        """
        # Attempts self.get(). If a value other than None occurs, return True
        if self.get(key) is not None:
            return True

        # If None is the result, return False.
        return False

    def remove(self, key: str) -> None:
        """
        Removes the given key and its associated value from the HM. If the key
        is not in the HM, the method does nothing.
        """
        # Step 1) If HM is empty, immediately return.
        if self._size == 0:
            return

        # Step 2) Finds the index of said key by putting it through the hash
        #   function. Assigns correct index value.
        hash_i = self.quad_prob(key, 'remove')

        # -- In this case, we've found the theoretical location of this key.
        #   Check it. If it is None, the key doesn't exist, and if the key at
        #   this index is not the key we're looking for, it probably DNE.
        if self._buckets[hash_i] is None or self._buckets[hash_i].key != key \
                or self._buckets[hash_i].is_tombstone:
            return

        # -- In this case, the HE exists. Make it a tombstone and decrement
        #   size.
        self._buckets[hash_i].is_tombstone = True
        self._size -= 1

    def clear(self) -> None:
        """
        Clears the contents of the hash map, but does not change the underlying
        hash table capacity.

        (No params)
        :return: None.
        """
        # Stores current capacity locally.
        curr_capacity = self._capacity

        # Creation of a new DA
        new_da = DynamicArray()

        # Appends items to the end of DA until capacity is same as self.
        for bucket in range(curr_capacity):
            new_da.append(None)

        # Uses this new_da as our new set of buckets.
        self._buckets = new_da

        # Resets size to 0 again.
        self._size = 0

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns a DA where each index contains a tuple of the key/value pairs
        stored in our HM.

        (No Params)
        :return: A new Dynamic Array object hosting tuples of all HM items.
        """
        # Creation of a new DA object:
        new_da = DynamicArray()

        # Iterates through each index of our HM and appends those values into
        # new HM.
        for hash_entry in self:
            new_da.append((hash_entry.key, hash_entry.value))

        # Returns new_da at end.
        return new_da

    def __iter__(self):
        """
        Create iterator for loop.
        """

        # Creation of an index parameter.
        self.da_i = 0

        # As long as this index is less than capacity and either None or a
        #   tombstone, skip ahead until we find a valid index.
        while self.da_i < self._capacity and \
                (not self._buckets[self.da_i] or
                 self._buckets[self.da_i].is_tombstone):
            self.da_i += 1

        # Return this.
        return self

    def __next__(self):
        """
        Obtain object at next index and advance iterator.
        """
        # If this index value becomes greater than or equal to our capacity,
        #   we've reached the end of the list. Stop.
        if self.da_i >= self._capacity:
            raise StopIteration

        # otherwise, test the value at this index and increment for next index.
        value = self._buckets[self.da_i]
        self.da_i += 1

        # If this index is None, or a tombstone and less than capacity, find
        #   valid next index (if not already so.)
        while self.da_i < self._capacity and \
                (not self._buckets[self.da_i] or
                 self._buckets[self.da_i].is_tombstone):
            self.da_i += 1

        # Returns valid value.
        return value


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(),
                  m.get_capacity())

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(),
                  m.get_capacity())

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

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(20, hash_function_1)
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity(), m.get('key1'),
          m.contains_key('key1'))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get('key1'),
          m.contains_key('key1'))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(75, hash_function_2)
    keys = [i for i in range(25, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        if m.table_load() > 0.5:
            print(
                f"Check that the load factor is acceptable after the call to resize_table().\n"
                f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(capacity, result, m.get_size(), m.get_capacity(),
              round(m.table_load(), 2))
    #
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
    m = HashMap(11, hash_function_1)
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

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.resize_table(2)
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(12)
    print(m.get_keys_and_values())

    print("\nPDF - __iter__(), __next__() example 1")
    print("---------------------")
    m = HashMap(10, hash_function_1)
    for i in range(5):
        m.put(str(i), str(i * 10))
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)

    print("\nPDF - __iter__(), __next__() example 2")
    print("---------------------")
    m = HashMap(10, hash_function_2)
    for i in range(5):
        m.put(str(i), str(i * 24))
    m.remove('0')
    m.remove('4')
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)
