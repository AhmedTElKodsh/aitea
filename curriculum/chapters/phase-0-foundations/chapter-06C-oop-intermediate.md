# Chapter 6C: Intermediate OOP — Building Flexible Hierarchies

<!--
METADATA
Phase: Python Bridge Module 1 (PBM-1)
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Foundation (Python Intermediate)
Prerequisites: Chapter 4, 6A, 6B
Builds Toward: Document Processing (Ch 16), Agent Tools (Ch 29)
Correctness Properties: Liskov Substitution, Interface Segregation

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

Picture this: You're building your AI document processing system. You need to handle PDFs, Word docs, CAD drawings, and more. Each document type has unique parsing logic, but they all share common operations: validation, metadata extraction, and error handling.

Your first instinct? Copy-paste the shared code into each document handler. 😱

But wait—what happens when you need to update the validation logic? You'd have to change it in 5 different places. Miss one? Bugs everywhere.

**This is where OOP intermediate patterns shine.** You'll learn to:
- Create a **base class** that handles shared logic once
- Let specialized classes **inherit** and extend only what's different
- Use **abstract methods** to enforce contracts ("every document handler MUST implement parse()")
- Expose **properties** that look like simple attributes but run smart logic behind the scenes

By the end of this chapter, you'll build a complete `DocumentProcessor` family with inheritance, abstractions, and properties—setting the foundation for your Civil Engineering document system. Let's dive in! 🚀

---

## Prerequisites Check

Before we proceed, make sure you're comfortable with:

✅ **Basic classes** (Chapter 4):
```python
class Document:
    def __init__(self, path):
        self.path = path
```

✅ **Error handling** (Chapter 6B):
```python
try:
    process_document()
except DocumentError as e:
    logger.error(f"Processing failed: {e}")
```

✅ **Decorators** (Chapter 6A) — we'll use `@property` and `@abstractmethod` here

If any of these feel shaky, take 10 minutes to review those chapters. This chapter builds directly on them! 🧩

---

## What You Already Know 🧩

You've been using OOP patterns all along without realizing it:

```python
# When you open a file:
with open("data.txt") as f:
    content = f.read()
```

**Behind the scenes:**
- `open()` returns a **file object** (instance of a class)
- All file objects **inherit** from `IOBase` (the base class)
- Different file types override specific methods (text files handle strings, binary files handle bytes)
- The `read()` method behaves differently depending on the file type

```python
# When you use pathlib:
from pathlib import Path

doc_path = Path("report.pdf")
print(doc_path.suffix)  # .pdf — looks like an attribute
print(doc_path.stem)    # report — but it's actually a computed property!
```

**What's happening:**
- `suffix` and `stem` are **properties**—they compute values on-the-fly
- You access them like attributes (`doc_path.suffix`) but they run methods behind the scenes
- This gives you a clean interface without exposing implementation details

You've been benefiting from inheritance and properties constantly. Now you'll learn to build these patterns yourself! 💡

---

## The Story: Why Class Hierarchies Matter

### The Problem

Ahmed is building his document processor. He starts with PDFs:

```python
class PDFProcessor:
    def __init__(self, path):
        self.path = path
        self._content = None

    def validate(self):
        """Check if file exists and is readable"""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")
        if not self.path.endswith('.pdf'):
            raise ValueError("Not a PDF file")

    def parse(self):
        """Extract text from PDF"""
        # PDF-specific parsing logic
        import PyPDF2
        with open(self.path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            self._content = "\n".join(page.extract_text() for page in reader.pages)

    def get_metadata(self):
        """Extract metadata"""
        return {
            "type": "pdf",
            "size": os.path.getsize(self.path),
            "pages": len(PyPDF2.PdfReader(self.path).pages)
        }
```

Works great! Now he needs to handle Word documents:

```python
class WordProcessor:
    def __init__(self, path):
        self.path = path
        self._content = None

    def validate(self):
        """Check if file exists and is readable"""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")
        if not self.path.endswith('.docx'):
            raise ValueError("Not a Word file")

    def parse(self):
        """Extract text from Word doc"""
        # Word-specific parsing logic
        import docx
        doc = docx.Document(self.path)
        self._content = "\n".join(para.text for para in doc.paragraphs)

    def get_metadata(self):
        """Extract metadata"""
        return {
            "type": "word",
            "size": os.path.getsize(self.path),
            "paragraphs": len(docx.Document(self.path).paragraphs)
        }
```

😰 **Houston, we have a problem:**
- `validate()` logic is nearly identical (only file extension differs)
- `get_metadata()` has duplicated `size` calculation
- If Ahmed needs to add logging, he'd have to change it in both classes
- When he adds CAD files, PowerPoint, images... the duplication multiplies

**This violates DRY (Don't Repeat Yourself)** and creates a maintenance nightmare.

### The Naive Solution

"I'll just make helper functions!"

```python
def validate_file(path, extension):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    if not path.endswith(extension):
        raise ValueError(f"Not a {extension} file")

class PDFProcessor:
    def validate(self):
        validate_file(self.path, '.pdf')
    # ... rest of the class

class WordProcessor:
    def validate(self):
        validate_file(self.path, '.docx')
    # ... rest of the class
```

**Better, but still problems:**
- Shared state (`self.path`, `self._content`) isn't centralized
- No guarantee that every processor implements `parse()` and `get_metadata()`
- Can't treat all processors uniformly (no common interface)
- Hard to add shared behavior like logging or caching

### The Elegant Solution: Inheritance + Abstraction

**The OOP way:**

```python
from abc import ABC, abstractmethod
from pathlib import Path

class DocumentProcessor(ABC):
    """Base class for all document processors"""

    def __init__(self, path: str):
        self.path = Path(path)
        self._content = None

    def validate(self):
        """Shared validation logic"""
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        if self.path.suffix != self.expected_extension:
            raise ValueError(f"Expected {self.expected_extension}, got {self.path.suffix}")

    @property
    @abstractmethod
    def expected_extension(self) -> str:
        """Subclasses must define their file extension"""
        pass

    @abstractmethod
    def parse(self):
        """Subclasses must implement parsing logic"""
        pass

    def get_metadata(self) -> dict:
        """Shared metadata extraction"""
        return {
            "type": self.__class__.__name__,
            "size": self.path.stat().st_size,
            "extension": self.path.suffix
        }

    @property
    def content(self) -> str:
        """Lazy-load content"""
        if self._content is None:
            self.parse()
        return self._content


class PDFProcessor(DocumentProcessor):
    """Handles PDF documents"""

    @property
    def expected_extension(self) -> str:
        return ".pdf"

    def parse(self):
        import PyPDF2
        with open(self.path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            self._content = "\n".join(page.extract_text() for page in reader.pages)


class WordProcessor(DocumentProcessor):
    """Handles Word documents"""

    @property
    def expected_extension(self) -> str:
        return ".docx"

    def parse(self):
        import docx
        doc = docx.Document(self.path)
        self._content = "\n".join(para.text for para in doc.paragraphs)
```

**🎉 Why this is beautiful:**

1. **Shared logic lives in one place** — `validate()` and `get_metadata()` are written once
2. **Subclasses focus only on what's unique** — PDF and Word processors only implement parsing
3. **Enforced contracts** — You *can't* create a subclass without implementing `parse()` and `expected_extension`
4. **Polymorphism** — You can treat all processors the same:

```python
def process_any_document(processor: DocumentProcessor):
    processor.validate()
    content = processor.content  # Works for PDF, Word, CAD, etc.
    metadata = processor.get_metadata()
    return content, metadata

# Usage
pdf_proc = PDFProcessor("report.pdf")
word_proc = WordProcessor("notes.docx")

# Same function handles both!
process_any_document(pdf_proc)
process_any_document(word_proc)
```

**This is the power of inheritance and abstraction.** Let's break down each piece step by step. 🔍

---

## Part 1: Inheritance Fundamentals

### The Parent-Child Relationship 🌳

Think of inheritance like a family tree. You inherit your parents' traits (eye color, height), but you're still your own person with unique characteristics.

```python
class Animal:
    """Parent class (base class, superclass)"""

    def __init__(self, name):
        self.name = name

    def speak(self):
        return "Some generic sound"

    def describe(self):
        return f"{self.name} is an animal"


class Dog(Animal):
    """Child class (subclass, derived class)"""

    def speak(self):
        """Override parent's speak method"""
        return "Woof!"


class Cat(Animal):
    """Another child class"""

    def speak(self):
        """Override parent's speak method"""
        return "Meow!"
```

**What's happening:**

```python
dog = Dog("Buddy")
cat = Cat("Whiskers")

# Inherited from Animal:
print(dog.describe())  # "Buddy is an animal"
print(cat.describe())  # "Whiskers is an animal"

# Overridden in subclass:
print(dog.speak())  # "Woof!"
print(cat.speak())  # "Meow!"
```

**Key concept:** Subclasses **inherit all methods and attributes** from the parent, but can **override** specific methods to change behavior.

### The `super()` Function — Extending Parent Behavior

Sometimes you don't want to *replace* the parent's method—you want to *extend* it.

```python
class Animal:
    def __init__(self, name):
        self.name = name
        print(f"Creating animal: {name}")


class Dog(Animal):
    def __init__(self, name, breed):
        # Call parent's __init__ first
        super().__init__(name)
        self.breed = breed
        print(f"Creating dog of breed: {breed}")


buddy = Dog("Buddy", "Golden Retriever")
# Output:
# Creating animal: Buddy
# Creating dog of breed: Golden Retriever

print(buddy.name)   # "Buddy" (from Animal)
print(buddy.breed)  # "Golden Retriever" (from Dog)
```

**Think of `super()` as calling your parent:**
- `super().__init__(name)` → "Hey parent, do your initialization first"
- Then you add your own child-specific logic

**Real-world analogy:** When you move out of your parents' house, you inherit their good habits (cleaning, budgeting) but add your own style (different furniture, new routines). You're not starting from scratch—you're building on what they taught you. 🏠

---

### 🔬 Try This! — Basic Inheritance

**Challenge:** Create a `Vehicle` base class and two subclasses: `Car` and `Bicycle`.

**Requirements:**
- `Vehicle` should have:
  - `__init__(brand, max_speed)`
  - `describe()` method returning a description
- `Car` should add:
  - `num_doors` attribute
  - Override `describe()` to include doors
- `Bicycle` should add:
  - `has_gears` boolean attribute
  - Override `describe()` to include gears

**Hints:**
1. Use `super().__init__()` in subclass constructors
2. Call `super().describe()` then add child-specific info
3. Test with: `Car("Toyota", 180, 4)` and `Bicycle("Trek", 30, True)`

<details>
<summary>💡 <strong>Solution</strong></summary>

```python
class Vehicle:
    def __init__(self, brand, max_speed):
        self.brand = brand
        self.max_speed = max_speed

    def describe(self):
        return f"{self.brand} vehicle (max speed: {self.max_speed} km/h)"


class Car(Vehicle):
    def __init__(self, brand, max_speed, num_doors):
        super().__init__(brand, max_speed)
        self.num_doors = num_doors

    def describe(self):
        base = super().describe()
        return f"{base} with {self.num_doors} doors"


class Bicycle(Vehicle):
    def __init__(self, brand, max_speed, has_gears):
        super().__init__(brand, max_speed)
        self.has_gears = has_gears

    def describe(self):
        base = super().describe()
        gears = "with gears" if self.has_gears else "single-speed"
        return f"{base} ({gears})"


# Test
car = Car("Toyota", 180, 4)
bike = Bicycle("Trek", 30, True)

print(car.describe())
# Toyota vehicle (max speed: 180 km/h) with 4 doors

print(bike.describe())
# Trek vehicle (max speed: 30 km/h) (with gears)
```

**Key takeaway:** Notice how we reused the parent's logic with `super().describe()` instead of rewriting it. This keeps code DRY! 🎯
</details>

---

## Part 2: Abstract Base Classes (ABC) — Enforcing Contracts

### The Problem with Plain Inheritance

Consider this:

```python
class DocumentProcessor:
    def process(self):
        self.validate()
        self.parse()
        return self.get_metadata()


class PDFProcessor(DocumentProcessor):
    def parse(self):
        # ... PDF parsing logic
        pass


class WordProcessor(DocumentProcessor):
    # Oops! Forgot to implement parse()
    pass
```

**What happens?**

```python
word_proc = WordProcessor()
word_proc.process()  # ❌ AttributeError: 'WordProcessor' object has no method 'parse'
```

**The error happens at runtime** (when you call `process()`), not when you define the class. By then, the bug might be deep in production code. 😱

### Abstract Classes to the Rescue 🦸

**Abstract Base Classes (ABC)** force you to implement required methods:

```python
from abc import ABC, abstractmethod

class DocumentProcessor(ABC):
    """Abstract base class for document processors"""

    @abstractmethod
    def parse(self):
        """Subclasses MUST implement this"""
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        """Subclasses MUST implement this"""
        pass

    def process(self):
        """Concrete method — shared by all subclasses"""
        self.parse()
        return self.get_metadata()


class PDFProcessor(DocumentProcessor):
    def parse(self):
        print("Parsing PDF...")

    def get_metadata(self):
        return {"type": "pdf"}


# This works fine:
pdf_proc = PDFProcessor()
pdf_proc.process()


class WordProcessor(DocumentProcessor):
    def parse(self):
        print("Parsing Word doc...")

    # Oops! Forgot get_metadata()


# This fails immediately when you try to instantiate:
word_proc = WordProcessor()
# ❌ TypeError: Can't instantiate abstract class WordProcessor with abstract method get_metadata
```

**🎉 The error happens at instantiation time**, not when you call methods. This catches bugs early!

**Key concepts:**
1. **ABC** — Import from `abc` module
2. **@abstractmethod** — Decorator marking methods that subclasses must implement
3. **Concrete methods** — Regular methods in abstract classes (like `process()`) are shared by all subclasses

**Analogy:** Abstract classes are like a job contract. The contract says "You MUST perform these duties" (abstract methods) and "These benefits are provided to everyone" (concrete methods). You can't sign a contract with missing duties! 📜

---

### 🔬 Try This! — Abstract Classes

**Challenge:** Create an abstract `Shape` class with subclasses `Circle` and `Rectangle`.

**Requirements:**
- `Shape` (abstract class):
  - Abstract method: `area()` → float
  - Abstract method: `perimeter()` → float
  - Concrete method: `describe()` → "This shape has area {area} and perimeter {perimeter}"
- `Circle`:
  - `__init__(radius)`
  - Implement `area()` and `perimeter()` using πr² and 2πr
- `Rectangle`:
  - `__init__(width, height)`
  - Implement `area()` and `perimeter()` using width×height and 2×(width+height)

**Hints:**
1. Import `ABC` and `abstractmethod` from `abc`
2. Use `math.pi` for π
3. Test with: `Circle(5)` and `Rectangle(4, 6)`

<details>
<summary>💡 <strong>Solution</strong></summary>

```python
from abc import ABC, abstractmethod
import math

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass

    def describe(self) -> str:
        """Concrete method — works for all shapes"""
        return f"This shape has area {self.area():.2f} and perimeter {self.perimeter():.2f}"


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


# Test
circle = Circle(5)
rectangle = Rectangle(4, 6)

print(circle.describe())
# This shape has area 78.54 and perimeter 31.42

print(rectangle.describe())
# This shape has area 24.00 and perimeter 20.00

# Try to create incomplete shape:
class Triangle(Shape):
    def area(self):
        return 10

# This will fail:
# tri = Triangle()  # ❌ TypeError: Can't instantiate abstract class Triangle with abstract method perimeter
```

**Key takeaway:** Abstract methods act as a safety net—you can't forget to implement required methods! 💪
</details>

---

## Part 3: Properties — Smart Attributes

### The Problem with Direct Attribute Access

Consider this simple class:

```python
class Document:
    def __init__(self, path):
        self.path = path
```

**Looks fine, but what if:**
1. You need to validate the path before setting it?
2. You want to compute the file size on-the-fly?
3. You need to log every time the path changes?

**Naive approach:**

```python
class Document:
    def set_path(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError("Path doesn't exist")
        self._path = path

    def get_path(self):
        return self._path

    def get_size(self):
        return os.path.getsize(self._path)


doc = Document()
doc.set_path("report.pdf")  # Ugly getter/setter syntax
print(doc.get_path())
print(doc.get_size())
```

😰 **Problems:**
- Awkward syntax (`get_path()`, `set_path()`)
- Users have to remember to use getters/setters
- Nothing stops them from directly accessing `doc._path` and bypassing validation

### Properties to the Rescue 🎩

**Properties let you write methods that look like attributes:**

```python
class Document:
    def __init__(self, path):
        self._path = None  # Private attribute
        self.path = path    # Triggers setter validation

    @property
    def path(self):
        """Getter — called when you access doc.path"""
        return self._path

    @path.setter
    def path(self, value):
        """Setter — called when you assign doc.path = '...'"""
        if not os.path.exists(value):
            raise FileNotFoundError(f"Path doesn't exist: {value}")
        self._path = value

    @property
    def size(self):
        """Computed property — calculated on-the-fly"""
        return os.path.getsize(self._path)


# Usage feels natural:
doc = Document("report.pdf")
print(doc.path)  # Calls the getter
print(doc.size)  # Calls the computed property

doc.path = "new_report.pdf"  # Calls the setter (validates path)
```

**🎉 Beautiful advantages:**
1. **Natural syntax** — `doc.path` instead of `doc.get_path()`
2. **Validation on assignment** — `doc.path = "invalid"` raises error immediately
3. **Computed values** — `doc.size` calculates on-the-fly without storing
4. **Backward compatibility** — If you later need validation, you can convert attributes to properties without breaking code

**Analogy:** Properties are like a vending machine. From the outside, you just insert money (set a value) and grab a snack (get a value). But inside, complex machinery validates your payment, checks inventory, and dispenses the product. The interface is simple; the implementation is smart. 🍫

---

### Read-Only Properties

Sometimes you want attributes that can be read but never changed:

```python
class Document:
    def __init__(self, path):
        self._path = path
        self._creation_time = time.time()

    @property
    def path(self):
        return self._path

    @property
    def creation_time(self):
        """Read-only property — no setter defined"""
        return self._creation_time


doc = Document("report.pdf")
print(doc.creation_time)  # ✅ Works

doc.creation_time = time.time()  # ❌ AttributeError: can't set attribute
```

**When to use read-only properties:**
- IDs (shouldn't change after creation)
- Creation timestamps
- Computed values that don't make sense to set (like `size`, `extension`)

---

### 🔬 Try This! — Properties with Validation

**Challenge:** Create a `Temperature` class with Celsius and Fahrenheit properties.

**Requirements:**
- `__init__(celsius)` — Initialize with Celsius temperature
- `celsius` property with getter and setter:
  - Setter validates that temperature > -273.15 (absolute zero)
- `fahrenheit` property (computed from Celsius):
  - Getter converts Celsius to Fahrenheit (F = C × 9/5 + 32)
  - Setter converts Fahrenheit to Celsius (C = (F - 32) × 5/9)
- `kelvin` property (read-only, computed from Celsius):
  - Getter returns Celsius + 273.15

**Hints:**
1. Use `@property` for getters
2. Use `@celsius.setter` and `@fahrenheit.setter` for setters
3. Store the temperature in one unit (Celsius) and compute the others
4. Test with: `temp = Temperature(25)`, then set `temp.fahrenheit = 86`

<details>
<summary>💡 <strong>Solution</strong></summary>

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = None
        self.celsius = celsius  # Use setter for validation

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature cannot be below absolute zero (-273.15°C)")
        self._celsius = value

    @property
    def fahrenheit(self):
        """Computed property — Celsius to Fahrenheit"""
        return self._celsius * 9/5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        """Convert Fahrenheit to Celsius and validate"""
        celsius = (value - 32) * 5/9
        self.celsius = celsius  # Use celsius setter for validation

    @property
    def kelvin(self):
        """Read-only computed property"""
        return self._celsius + 273.15


# Test
temp = Temperature(25)
print(f"{temp.celsius}°C = {temp.fahrenheit}°F = {temp.kelvin}K")
# 25°C = 77.0°F = 298.15K

temp.fahrenheit = 86
print(f"{temp.celsius}°C = {temp.fahrenheit}°F = {temp.kelvin}K")
# 30.0°C = 86.0°F = 303.15K

# Try invalid temperature:
# temp.celsius = -300  # ❌ ValueError: Temperature cannot be below absolute zero

# Try to set kelvin (read-only):
# temp.kelvin = 300  # ❌ AttributeError: can't set attribute
```

**Key takeaway:** Properties let you expose a clean interface (just `temp.celsius`, `temp.fahrenheit`) while keeping complex logic hidden. Perfect for conversions, validations, and computed values! 🌡️
</details>

---

## Transition: Class Methods vs Instance Methods

We've covered inheritance, abstract classes, and properties—all centered on **instances** (individual objects). But sometimes you need methods that work at the **class level**, not tied to any specific instance.

**Example scenario:**
- You want to create a `Document` from a file path or from raw text
- You need factory methods that return different types of processors based on file extension
- You want to count how many documents have been created

For these cases, we need **class methods** and **static methods**. Let's explore when to use each! 🔧

---

## Part 4: Class Methods, Instance Methods, and Static Methods

### Instance Methods (What You Already Know)

**Instance methods** are the default—they operate on a specific instance:

```python
class Document:
    def __init__(self, path):
        self.path = path

    def read(self):
        """Instance method — needs self"""
        with open(self.path) as f:
            return f.read()


doc = Document("report.pdf")
content = doc.read()  # Called on an instance
```

**Key:** Receives `self` (the instance) as the first parameter.

---

### Class Methods — Factory Functions and Class-Level Operations

**Class methods** operate on the class itself, not instances:

```python
class Document:
    total_created = 0  # Class variable (shared by all instances)

    def __init__(self, path, content):
        self.path = path
        self.content = content
        Document.total_created += 1

    @classmethod
    def from_file(cls, path):
        """Factory method — creates instance from file"""
        with open(path) as f:
            content = f.read()
        return cls(path, content)  # cls is the class itself

    @classmethod
    def from_text(cls, text):
        """Factory method — creates instance from raw text"""
        return cls("in-memory", text)

    @classmethod
    def get_total_created(cls):
        """Access class variable"""
        return cls.total_created


# Usage:
doc1 = Document.from_file("report.pdf")  # Factory method
doc2 = Document.from_text("Hello world")  # Another factory method

print(Document.get_total_created())  # 2
```

**Key differences:**
- Use `@classmethod` decorator
- First parameter is `cls` (the class itself), not `self`
- Can access class variables and create new instances
- Called on the class: `Document.from_file()`

**When to use class methods:**
1. **Factory methods** — Alternative constructors (`from_file`, `from_dict`, `from_json`)
2. **Class-level operations** — Counting instances, resetting state, etc.

**Real-world example:**

```python
from datetime import datetime

class LogEntry:
    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(data['timestamp'], data['message'])

    @classmethod
    def now(cls, message):
        """Create log entry with current timestamp"""
        return cls(datetime.now(), message)


# Clean factory methods:
log1 = LogEntry.from_json('{"timestamp": "2024-01-16", "message": "Error"}')
log2 = LogEntry.now("User logged in")
```

---

### Static Methods — Utility Functions

**Static methods** don't access instance or class data—they're just regular functions grouped inside a class:

```python
class DocumentProcessor:
    @staticmethod
    def is_valid_extension(path):
        """Utility function — doesn't need self or cls"""
        return path.endswith(('.pdf', '.docx', '.txt'))

    @staticmethod
    def sanitize_filename(filename):
        """Remove invalid characters"""
        return "".join(c for c in filename if c.isalnum() or c in "._- ")


# Called on the class (no instance needed):
if DocumentProcessor.is_valid_extension("report.pdf"):
    safe_name = DocumentProcessor.sanitize_filename("my file!@#.pdf")
    print(safe_name)  # "my file.pdf"
```

**Key differences:**
- Use `@staticmethod` decorator
- No `self` or `cls` parameter
- Cannot access instance or class variables
- Just a regular function logically grouped with the class

**When to use static methods:**
- Utility functions related to the class but don't need access to instance/class data
- Validators, formatters, converters

**Honestly?** Most of the time, static methods can just be module-level functions. Use them when they're conceptually part of the class's API but don't need `self` or `cls`.

---

### Quick Comparison

| Method Type | Decorator | First Parameter | Use Case | Example |
|-------------|-----------|-----------------|----------|---------|
| **Instance** | None | `self` | Operate on instance data | `doc.read()` |
| **Class** | `@classmethod` | `cls` | Factory methods, class-level operations | `Document.from_file()` |
| **Static** | `@staticmethod` | None | Utility functions | `DocumentProcessor.is_valid_extension()` |

**Analogy:**
- **Instance method** = Personal task (you brush *your* teeth)
- **Class method** = Family task (someone calls a family meeting)
- **Static method** = General advice (a universal life tip that applies to anyone)

---

### 🔬 Try This! — Factory Methods

**Challenge:** Create a `User` class with factory methods for different creation scenarios.

**Requirements:**
- `User` class:
  - `__init__(username, email, role)`
  - Class variable `total_users` (incremented in `__init__`)
- Class methods:
  - `from_dict(data)` — Create user from dict like `{"username": "ahmed", "email": "...", "role": "admin"}`
  - `create_admin(username, email)` — Factory for admin users (role="admin")
  - `get_total_users()` — Return total users created
- Static method:
  - `is_valid_email(email)` — Return True if email contains "@"

**Hints:**
1. Use `@classmethod` for factory methods (they return `cls(...)`)
2. Use `@staticmethod` for validation (doesn't need `self` or `cls`)
3. Increment `User.total_users` in `__init__`
4. Test with: `User.create_admin("ahmed", "ahmed@example.com")` and `User.from_dict({...})`

<details>
<summary>💡 <strong>Solution</strong></summary>

```python
class User:
    total_users = 0  # Class variable

    def __init__(self, username, email, role):
        self.username = username
        self.email = email
        self.role = role
        User.total_users += 1

    @classmethod
    def from_dict(cls, data):
        """Factory method — create from dictionary"""
        return cls(data['username'], data['email'], data['role'])

    @classmethod
    def create_admin(cls, username, email):
        """Factory method — shortcut for admin users"""
        return cls(username, email, role="admin")

    @classmethod
    def get_total_users(cls):
        """Access class variable"""
        return cls.total_users

    @staticmethod
    def is_valid_email(email):
        """Utility function — validate email format"""
        return "@" in email


# Test factory methods:
admin = User.create_admin("ahmed", "ahmed@example.com")
print(f"{admin.username} is an {admin.role}")  # ahmed is an admin

user_data = {"username": "john", "email": "john@example.com", "role": "viewer"}
user = User.from_dict(user_data)
print(f"{user.username} is a {user.role}")  # john is a viewer

# Test class method:
print(f"Total users: {User.get_total_users()}")  # Total users: 2

# Test static method:
print(User.is_valid_email("test@example.com"))  # True
print(User.is_valid_email("invalid"))  # False
```

**Key takeaway:** Factory methods (`@classmethod`) give you clean, expressive ways to create instances without cluttering `__init__` with multiple optional parameters. Static methods keep related utilities close to the class. 🏭
</details>

---

## Part 5: When to Use Classes vs Functions

**The big question:** Not everything needs to be a class. When should you use classes vs plain functions?

### Use Functions When:

✅ **Stateless operations** — No data to store between calls

```python
# Good — simple, stateless function
def calculate_area(width, height):
    return width * height
```

✅ **One-off tasks** — Used once and done

```python
# Good — utility function
def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
```

✅ **Composable transformations** — Chain functions together

```python
# Good — functional pipeline
result = (
    load_data(path)
    .pipe(clean_data)
    .pipe(transform_data)
    .pipe(save_data)
)
```

### Use Classes When:

✅ **State management** — Need to store and modify data over time

```python
# Good — maintains state across operations
class DatabaseConnection:
    def __init__(self, connection_string):
        self.connection = create_connection(connection_string)
        self.is_open = True

    def query(self, sql):
        if not self.is_open:
            raise ConnectionError("Connection closed")
        return self.connection.execute(sql)

    def close(self):
        self.connection.close()
        self.is_open = False
```

✅ **Related operations on shared data** — Multiple methods working on the same data

```python
# Good — methods share document data
class DocumentAnalyzer:
    def __init__(self, text):
        self.text = text
        self._word_count = None
        self._sentences = None

    def word_count(self):
        if self._word_count is None:
            self._word_count = len(self.text.split())
        return self._word_count

    def sentence_count(self):
        if self._sentences is None:
            self._sentences = self.text.split('.')
        return len(self._sentences)
```

✅ **Polymorphism** — Need different implementations of the same interface

```python
# Good — different processors with same interface
class PDFProcessor(DocumentProcessor):
    def parse(self):
        # PDF-specific logic
        pass

class WordProcessor(DocumentProcessor):
    def parse(self):
        # Word-specific logic
        pass

# Can treat all processors uniformly:
def process_document(processor: DocumentProcessor):
    processor.parse()
```

✅ **Resource management** — Need setup/teardown (context managers)

```python
# Good — manages file lifecycle
class ManagedFile:
    def __init__(self, path):
        self.path = path
        self.file = None

    def __enter__(self):
        self.file = open(self.path)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
```

### Avoid Over-Engineering

**❌ Bad — Unnecessary class for stateless operation:**

```python
class AreaCalculator:
    def calculate(self, width, height):
        return width * height

calc = AreaCalculator()
area = calc.calculate(10, 20)  # Just use a function!
```

**✅ Good — Simple function:**

```python
def calculate_area(width, height):
    return width * height

area = calculate_area(10, 20)
```

**Rule of thumb:** Start with functions. Promote to classes when you need state, polymorphism, or resource management. Don't create classes "just because." 🎯

---

## Bringing It All Together: Complete Document Processing System

Let's combine everything we've learned into a realistic Civil Engineering document processor:

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentError(Exception):
    """Base exception for document processing"""
    pass


class InvalidDocumentError(DocumentError):
    """Raised when document format is invalid"""
    pass


class DocumentProcessor(ABC):
    """
    Abstract base class for all document processors.

    Provides shared functionality:
    - Path validation
    - Metadata extraction
    - Lazy content loading
    - Factory method for creating correct processor type
    """

    total_processed = 0  # Class variable

    def __init__(self, path: str):
        self._path = None
        self.path = path  # Use setter for validation
        self._content = None
        DocumentProcessor.total_processed += 1

    @property
    def path(self) -> Path:
        """Path to the document"""
        return self._path

    @path.setter
    def path(self, value: str):
        """Validate and set path"""
        path = Path(value)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {value}")
        if path.suffix != self.expected_extension:
            raise InvalidDocumentError(
                f"Expected {self.expected_extension}, got {path.suffix}"
            )
        self._path = path
        logger.info(f"Document loaded: {path.name}")

    @property
    @abstractmethod
    def expected_extension(self) -> str:
        """File extension this processor handles (e.g., '.pdf')"""
        pass

    @abstractmethod
    def parse(self) -> str:
        """Parse document and return text content"""
        pass

    @property
    def content(self) -> str:
        """Lazy-load content (only parse once)"""
        if self._content is None:
            logger.info(f"Parsing {self.path.name}...")
            self._content = self.parse()
        return self._content

    @property
    def size_mb(self) -> float:
        """Document size in megabytes"""
        size_bytes = self._path.stat().st_size
        return size_bytes / (1024 * 1024)

    def get_metadata(self) -> dict:
        """Extract document metadata"""
        return {
            "filename": self._path.name,
            "extension": self._path.suffix,
            "size_mb": round(self.size_mb, 2),
            "processor": self.__class__.__name__
        }

    @classmethod
    def from_path(cls, path: str):
        """
        Factory method: Create appropriate processor based on file extension.

        Example:
            processor = DocumentProcessor.from_path("report.pdf")
            # Returns PDFProcessor instance
        """
        extension = Path(path).suffix.lower()

        processors = {
            '.pdf': PDFProcessor,
            '.docx': WordProcessor,
            '.txt': TextProcessor
        }

        processor_class = processors.get(extension)
        if processor_class is None:
            raise InvalidDocumentError(f"No processor for {extension} files")

        return processor_class(path)

    @classmethod
    def get_total_processed(cls) -> int:
        """Return total documents processed"""
        return cls.total_processed

    @staticmethod
    def is_supported(path: str) -> bool:
        """Check if file type is supported"""
        extension = Path(path).suffix.lower()
        return extension in ['.pdf', '.docx', '.txt']


class PDFProcessor(DocumentProcessor):
    """Handles PDF documents"""

    @property
    def expected_extension(self) -> str:
        return ".pdf"

    def parse(self) -> str:
        """Extract text from PDF"""
        # Placeholder (would use PyPDF2 in real implementation)
        return f"[PDF content from {self.path.name}]"

    def get_metadata(self) -> dict:
        """Add PDF-specific metadata"""
        metadata = super().get_metadata()
        metadata['page_count'] = 10  # Placeholder
        return metadata


class WordProcessor(DocumentProcessor):
    """Handles Microsoft Word documents"""

    @property
    def expected_extension(self) -> str:
        return ".docx"

    def parse(self) -> str:
        """Extract text from Word document"""
        # Placeholder (would use python-docx in real implementation)
        return f"[Word content from {self.path.name}]"


class TextProcessor(DocumentProcessor):
    """Handles plain text files"""

    @property
    def expected_extension(self) -> str:
        return ".txt"

    def parse(self) -> str:
        """Read text file"""
        return self.path.read_text(encoding='utf-8')


# Usage example:
def process_document(path: str):
    """Process any supported document"""
    # Check if supported
    if not DocumentProcessor.is_supported(path):
        print(f"❌ Unsupported file type: {path}")
        return

    # Create appropriate processor (factory method)
    processor = DocumentProcessor.from_path(path)

    # Access metadata
    metadata = processor.get_metadata()
    print(f"📄 {metadata['filename']} ({metadata['size_mb']} MB)")

    # Lazy-load content (only parsed when accessed)
    content = processor.content
    print(f"Content preview: {content[:100]}...")

    return processor


# Example usage:
if __name__ == "__main__":
    # Test files (create these for testing)
    files = ["report.pdf", "notes.docx", "data.txt"]

    for file_path in files:
        try:
            processor = process_document(file_path)
        except (FileNotFoundError, InvalidDocumentError) as e:
            print(f"❌ Error: {e}")

    print(f"\nTotal documents processed: {DocumentProcessor.get_total_processed()}")
```

**What this demonstrates:**

1. ✅ **Abstract base class** — `DocumentProcessor` enforces contracts
2. ✅ **Inheritance** — `PDFProcessor`, `WordProcessor`, `TextProcessor` reuse shared logic
3. ✅ **Properties** — `path`, `content`, `size_mb` with validation and lazy loading
4. ✅ **Class methods** — `from_path()` factory, `get_total_processed()`
5. ✅ **Static methods** — `is_supported()` utility function
6. ✅ **Error handling** — Custom exceptions with meaningful messages
7. ✅ **Polymorphism** — `process_document()` works with any processor type

**Try running this code!** Create test files (`report.pdf`, `notes.docx`, `data.txt`) and watch the processors handle them uniformly. This is the foundation for your Civil Engineering document system! 🏗️

---

## Common Mistakes and How to Avoid Them

### Mistake 1: Forgetting `super().__init__()`

❌ **Wrong:**
```python
class PDFProcessor(DocumentProcessor):
    def __init__(self, path):
        self.pdf_version = "1.7"  # Forgot to call parent's __init__!
```

✅ **Correct:**
```python
class PDFProcessor(DocumentProcessor):
    def __init__(self, path):
        super().__init__(path)  # Initialize parent first
        self.pdf_version = "1.7"
```

**Why it matters:** Parent's initialization sets up critical state (`self.path`, `self._content`). Skipping it causes `AttributeError` later.

---

### Mistake 2: Overriding Methods Without Calling `super()`

❌ **Wrong:**
```python
class PDFProcessor(DocumentProcessor):
    def get_metadata(self):
        return {"page_count": 10}  # Lost all parent metadata!
```

✅ **Correct:**
```python
class PDFProcessor(DocumentProcessor):
    def get_metadata(self):
        metadata = super().get_metadata()  # Get parent metadata first
        metadata['page_count'] = 10  # Add child-specific data
        return metadata
```

**Why it matters:** You want to **extend** parent functionality, not **replace** it entirely.

---

### Mistake 3: Accessing Private Attributes Directly

❌ **Wrong:**
```python
doc = Document("report.pdf")
doc._path = Path("invalid.txt")  # Bypassed validation!
```

✅ **Correct:**
```python
doc = Document("report.pdf")
doc.path = "invalid.txt"  # Triggers setter validation
```

**Why it matters:** Properties and setters exist to enforce invariants. Direct access to `_path` bypasses validation.

**Convention:** `_attribute` signals "private—don't touch directly." Use the public property instead.

---

### Mistake 4: Using Mutable Default Arguments

❌ **Wrong:**
```python
class DocumentProcessor:
    def __init__(self, path, tags=[]):
        self.path = path
        self.tags = tags  # Shared across instances!


doc1 = DocumentProcessor("a.pdf")
doc1.tags.append("urgent")

doc2 = DocumentProcessor("b.pdf")
print(doc2.tags)  # ['urgent'] — WTF?!
```

✅ **Correct:**
```python
class DocumentProcessor:
    def __init__(self, path, tags=None):
        self.path = path
        self.tags = tags if tags is not None else []


doc1 = DocumentProcessor("a.pdf")
doc1.tags.append("urgent")

doc2 = DocumentProcessor("b.pdf")
print(doc2.tags)  # [] — correct!
```

**Why it matters:** Default arguments are evaluated **once** at function definition, not each time the function is called. Lists/dicts are mutable and shared across calls.

**Rule:** Never use mutable defaults (`[]`, `{}`). Use `None` and create new instances in the function body.

---

### Mistake 5: Abstract Class Without Abstract Methods

❌ **Wrong:**
```python
from abc import ABC

class DocumentProcessor(ABC):
    def parse(self):
        raise NotImplementedError("Subclasses must implement parse()")


# This works (but shouldn't):
processor = DocumentProcessor()
```

✅ **Correct:**
```python
from abc import ABC, abstractmethod

class DocumentProcessor(ABC):
    @abstractmethod
    def parse(self):
        """Subclasses must implement this"""
        pass


# This fails at instantiation:
processor = DocumentProcessor()  # ❌ TypeError: Can't instantiate abstract class
```

**Why it matters:** Without `@abstractmethod`, Python allows instantiation of incomplete classes. Use the decorator to catch bugs early!

---

## Quick Reference Card

### Inheritance Basics

```python
class Parent:
    def __init__(self, x):
        self.x = x

class Child(Parent):
    def __init__(self, x, y):
        super().__init__(x)  # Call parent's __init__
        self.y = y
```

### Abstract Base Classes

```python
from abc import ABC, abstractmethod

class Base(ABC):
    @abstractmethod
    def required_method(self):
        pass

class Concrete(Base):
    def required_method(self):
        return "Implemented!"
```

### Properties

```python
class MyClass:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value < 0:
            raise ValueError("Must be positive")
        self._value = new_value
```

### Class Methods and Static Methods

```python
class MyClass:
    total = 0

    @classmethod
    def from_dict(cls, data):
        return cls(data['field'])

    @staticmethod
    def is_valid(value):
        return value > 0
```

---

## Verification

Before moving on, test your understanding:

```python
# Create test.py with this code:

from abc import ABC, abstractmethod

class Vehicle(ABC):
    total_vehicles = 0

    def __init__(self, brand, max_speed):
        self._brand = brand
        self._max_speed = max_speed
        Vehicle.total_vehicles += 1

    @property
    def brand(self):
        return self._brand

    @property
    @abstractmethod
    def vehicle_type(self) -> str:
        pass

    @abstractmethod
    def describe(self) -> str:
        pass

    @classmethod
    def get_total_vehicles(cls):
        return cls.total_vehicles


class Car(Vehicle):
    def __init__(self, brand, max_speed, num_doors):
        super().__init__(brand, max_speed)
        self.num_doors = num_doors

    @property
    def vehicle_type(self):
        return "Car"

    def describe(self):
        return f"{self.brand} {self.vehicle_type} with {self.num_doors} doors"


class Motorcycle(Vehicle):
    def __init__(self, brand, max_speed, has_sidecar):
        super().__init__(brand, max_speed)
        self.has_sidecar = has_sidecar

    @property
    def vehicle_type(self):
        return "Motorcycle"

    def describe(self):
        sidecar = "with sidecar" if self.has_sidecar else "without sidecar"
        return f"{self.brand} {self.vehicle_type} {sidecar}"


# Test
car = Car("Toyota", 180, 4)
bike = Motorcycle("Harley", 200, False)

print(car.describe())
print(bike.describe())
print(f"Total vehicles: {Vehicle.get_total_vehicles()}")
```

**Run it:**
```bash
python test.py
```

**Expected output:**
```
Toyota Car with 4 doors
Harley Motorcycle without sidecar
Total vehicles: 2
```

**If it works, you understand:**
✅ Inheritance with `super().__init__()`
✅ Abstract base classes with `@abstractmethod`
✅ Properties with `@property`
✅ Class methods with `@classmethod`

You're ready to move forward! 💪

---

## Assessment

### Quick Check Questions

1. **What's the difference between `@abstractmethod` and a regular method that raises `NotImplementedError`?**
   <details>
   <summary>Answer</summary>

   `@abstractmethod` prevents instantiation of the abstract class (error at class creation), while `NotImplementedError` only fails when the method is called (error at runtime). Abstract methods catch bugs earlier.
   </details>

2. **When should you use `@property` vs a regular method?**
   <details>
   <summary>Answer</summary>

   Use `@property` for:
   - Computed attributes (looks like data, but calculated on-the-fly)
   - Attributes that need validation on assignment
   - Read-only attributes

   Use regular methods for:
   - Operations that modify state
   - Operations that take parameters (beyond `self`)
   - Actions that have side effects (like saving to disk)
   </details>

3. **What's the difference between `@classmethod` and `@staticmethod`?**
   <details>
   <summary>Answer</summary>

   - `@classmethod`: Receives `cls` (the class itself), can access class variables and create instances. Use for factory methods.
   - `@staticmethod`: Receives no special first parameter, can't access class or instance data. Use for utility functions.
   </details>

4. **Why use `super().__init__()` instead of calling the parent class directly?**
   <details>
   <summary>Answer</summary>

   `super()` handles multiple inheritance correctly and makes code more maintainable. If the parent class name changes, you only update the class definition, not every `__init__` call.

   ```python
   # Good — flexible
   super().__init__(x)

   # Bad — brittle
   ParentClass.__init__(self, x)
   ```
   </details>

5. **When should you use a class instead of plain functions?**
   <details>
   <summary>Answer</summary>

   Use classes when you need:
   - **State management** — data persists between method calls
   - **Polymorphism** — different implementations of the same interface
   - **Resource management** — setup/teardown logic
   - **Related operations** — multiple methods working on shared data

   Use functions for stateless, one-off operations.
   </details>

---

### Coding Challenge: Civil Engineering Document Analyzer

**Your mission:** Build a document analysis system for Civil Engineering projects using inheritance, abstract classes, and properties.

**Requirements:**

1. **Create abstract base class `DocumentAnalyzer`:**
   - Abstract method: `analyze() -> dict`
   - Property: `word_count` (lazy-loaded, computed from content)
   - Property: `file_size_mb` (read-only, computed from path)
   - Class variable: `total_analyzed` (incremented in `__init__`)
   - Class method: `get_total_analyzed()`

2. **Create concrete subclasses:**
   - `StructuralReportAnalyzer`:
     - Analyzes structural engineering reports (`.txt` files)
     - `analyze()` returns: `{"type": "structural", "keywords": ["beam", "column", "load"], "word_count": ...}`
   - `CADDocumentAnalyzer`:
     - Analyzes CAD documentation (`.txt` files with "CAD" in filename)
     - `analyze()` returns: `{"type": "cad", "dimensions_found": 5, "word_count": ...}`

3. **Add factory method:**
   - `DocumentAnalyzer.from_file(path)` — Detect analyzer type based on filename:
     - If filename contains "CAD" → `CADDocumentAnalyzer`
     - Otherwise → `StructuralReportAnalyzer`

4. **Test with sample files:**
   - Create `structural_report.txt` with content: "The beam supports a load of 500kN. The column is critical."
   - Create `CAD_drawing_notes.txt` with content: "Dimension A: 10m, Dimension B: 5m, Height: 3m."

**Hints:**
- Use `Path(path).stat().st_size` for file size
- Use `path.read_text()` for content
- Count words with `len(content.split())`
- For CAD dimensions, count occurrences of "Dimension" or numbers

<details>
<summary>💡 <strong>Solution</strong></summary>

```python
from abc import ABC, abstractmethod
from pathlib import Path

class DocumentAnalyzer(ABC):
    """Abstract base class for document analyzers"""

    total_analyzed = 0

    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        self._content = None
        self._word_count = None
        DocumentAnalyzer.total_analyzed += 1

    @property
    def content(self) -> str:
        """Lazy-load file content"""
        if self._content is None:
            self._content = self.path.read_text(encoding='utf-8')
        return self._content

    @property
    def word_count(self) -> int:
        """Computed property — count words in content"""
        if self._word_count is None:
            self._word_count = len(self.content.split())
        return self._word_count

    @property
    def file_size_mb(self) -> float:
        """Read-only property — file size in MB"""
        size_bytes = self.path.stat().st_size
        return size_bytes / (1024 * 1024)

    @abstractmethod
    def analyze(self) -> dict:
        """Analyze document and return results"""
        pass

    @classmethod
    def from_file(cls, path: str):
        """Factory method — create appropriate analyzer based on filename"""
        if "CAD" in Path(path).name:
            return CADDocumentAnalyzer(path)
        else:
            return StructuralReportAnalyzer(path)

    @classmethod
    def get_total_analyzed(cls) -> int:
        """Return total documents analyzed"""
        return cls.total_analyzed


class StructuralReportAnalyzer(DocumentAnalyzer):
    """Analyzes structural engineering reports"""

    def analyze(self) -> dict:
        """Find structural keywords"""
        content_lower = self.content.lower()
        keywords = ["beam", "column", "load"]
        found_keywords = [kw for kw in keywords if kw in content_lower]

        return {
            "type": "structural",
            "keywords": found_keywords,
            "word_count": self.word_count,
            "file_size_mb": round(self.file_size_mb, 4)
        }


class CADDocumentAnalyzer(DocumentAnalyzer):
    """Analyzes CAD documentation"""

    def analyze(self) -> dict:
        """Count dimensions found"""
        dimensions_found = self.content.lower().count("dimension")

        return {
            "type": "cad",
            "dimensions_found": dimensions_found,
            "word_count": self.word_count,
            "file_size_mb": round(self.file_size_mb, 4)
        }


# Create test files
Path("structural_report.txt").write_text(
    "The beam supports a load of 500kN. The column is critical."
)
Path("CAD_drawing_notes.txt").write_text(
    "Dimension A: 10m, Dimension B: 5m, Height: 3m."
)

# Test the analyzers
files = ["structural_report.txt", "CAD_drawing_notes.txt"]

for file_path in files:
    analyzer = DocumentAnalyzer.from_file(file_path)
    result = analyzer.analyze()
    print(f"\n📄 {file_path}")
    print(f"   Type: {result['type']}")
    print(f"   Word Count: {result['word_count']}")
    print(f"   File Size: {result['file_size_mb']} MB")

    if result['type'] == 'structural':
        print(f"   Keywords Found: {', '.join(result['keywords'])}")
    elif result['type'] == 'cad':
        print(f"   Dimensions Found: {result['dimensions_found']}")

print(f"\n📊 Total documents analyzed: {DocumentAnalyzer.get_total_analyzed()}")
```

**Expected output:**
```
📄 structural_report.txt
   Type: structural
   Word Count: 12
   File Size: 0.0001 MB
   Keywords Found: beam, load, column

📄 CAD_drawing_notes.txt
   Type: cad
   Word Count: 10
   File Size: 0.0001 MB
   Dimensions Found: 2

📊 Total documents analyzed: 2
```

**What this demonstrates:**
- ✅ Abstract base class with `@abstractmethod`
- ✅ Properties: `word_count` (lazy-loaded), `file_size_mb` (read-only)
- ✅ Inheritance: Subclasses reuse parent's properties and methods
- ✅ Factory method: `from_file()` creates correct analyzer type
- ✅ Class variable tracking: `total_analyzed`
- ✅ Polymorphism: Same interface for different document types

**You've built a production-ready document analysis system!** 🎉
</details>

---

## What's Next?

You've mastered intermediate OOP patterns—inheritance, abstract classes, properties, and method types. These are the building blocks for complex systems.

**In the next chapter (Chapter 7: Your First LLM Call)**, you'll apply these patterns to:
- Create a `BaseLLMClient` abstract class
- Implement `OpenAIClient`, `AnthropicClient`, etc. as subclasses
- Use properties for API keys and configuration
- Build factory methods for provider selection

**But first, take a break!** You've learned a LOT:
- How to build flexible class hierarchies with inheritance
- How to enforce contracts with abstract base classes
- How to create smart attributes with properties
- When to use classes vs functions

These patterns are everywhere in professional Python code. You're now equipped to read and write production-quality OOP! 💼

**Preview of your Civil Engineering system:**
```python
# Chapter 54 — Final system will look like this:

class DocumentProcessor(ABC):
    @abstractmethod
    def parse(self): pass

class PDFProcessor(DocumentProcessor): ...
class CADProcessor(DocumentProcessor): ...

class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt): pass

class OpenAIClient(LLMClient): ...
class AnthropicClient(LLMClient): ...

# Compose them together:
processor = DocumentProcessor.from_file("blueprint.pdf")
llm = LLMClient.from_provider("openai")
result = llm.generate(f"Analyze this: {processor.content}")
```

**You're building the foundation right now!** 🏗️

---

## Summary

**What you learned:**

1. ✅ **Inheritance** — Reuse code by extending parent classes with `class Child(Parent)`
2. ✅ **`super()`** — Call parent methods to extend (not replace) functionality
3. ✅ **Abstract Base Classes** — Enforce contracts with `ABC` and `@abstractmethod`
4. ✅ **Properties** — Create smart attributes with `@property` and setters for validation/computation
5. ✅ **Class Methods** — Factory functions and class-level operations with `@classmethod`
6. ✅ **Static Methods** — Utility functions grouped with classes using `@staticmethod`
7. ✅ **Classes vs Functions** — When to use each for clean, maintainable code

**Key takeaway:** OOP patterns let you write code once and reuse it everywhere. Inheritance eliminates duplication, abstract classes enforce contracts, and properties create clean interfaces. These patterns scale from small scripts to massive systems—like the AI document processor you're building! 🚀

**You got this!** 💪 Now rest up, then dive into Chapter 7 where we'll make our first LLM API call! 🤖
