import math
from enum import Enum
from typing import List
import warnings
import random
import itertools

# THINGS THAT ARE NOT CHECKED!!!!
# - if Stammodule where picked correctly
# - Stammodule are NOT excluded from the amount of ects reagrding the required ects in lectures in the specialization, which is wrong
# - when over 120 ects total, the module with the worst ects is cut off, I think, that is how it works, but it is ignored if 
#   the module would not meet the needed requirements without the cut off ects

class SubjectType(Enum):
    LECTURE = 0
    SEMINAR = 1
    PRACTICAL = 2
    OTHER = 3

class MODULES(Enum):
    THESIS = 0
    ELECTIVE = 1
    MINOR = 2
    INTERDISCIPLINARY = 3

    THEORETICAL = 4
    AI = 5
    ALGORITHM_ENGINEERING = 6
    CRYPTOGRAPHY = 7
    DATA_SCIENCE = 8
    EMBEDDED_SYSTEMS = 9
    ROBOTICS = 10
    SOFTWARE_ENGINEERING = 11
    TELEMATICS = 12


    def get_non_specializaiton_modules():
        return [MODULES.THESIS, MODULES.ELECTIVE, MODULES.MINOR, MODULES.INTERDISCIPLINARY]

class Subject:
    def __init__(self, name: str, grade: float, ects: int, subject_type: SubjectType, possible_modules: List[MODULES]=[MODULES.ELECTIVE], add_elective_to_possible_modules: bool=True, weight: float=1):
        self.name = name
        self.grade = grade
        self.ects = ects
        self.subject_type = subject_type
        self.possible_modules = possible_modules
        self.weight = weight

        if add_elective_to_possible_modules and \
            not MODULES.ELECTIVE in possible_modules and \
            not MODULES.THESIS in possible_modules and \
            not MODULES.INTERDISCIPLINARY in possible_modules and \
            not MODULES.MINOR in possible_modules:

            self.possible_modules.append(MODULES.ELECTIVE)
        self.current_module = possible_modules[0]

    @property 
    def weight(self):
        if self.current_module == MODULES.INTERDISCIPLINARY:
            return 0
        return self._weight
    
    @weight.setter
    def weight(self, value: float):
        self._weight = value

class GradeTable:
    def __init__(self, first_specialization: MODULES, second_specialization: MODULES):
        self.subjects: List[Subject] = []
        if first_specialization == second_specialization:
            raise RuntimeError("first and second specialization can not be the same")
         
        if first_specialization in MODULES.get_non_specializaiton_modules() or second_specialization in MODULES.get_non_specializaiton_modules():
            raise RuntimeError("specializations can not be one of: ", MODULES.get_non_specializaiton_modules())
        self.first_specialization = first_specialization
        self.second_specialization = second_specialization

    def get_subject_by_name(self, name):
        for s in self.subjects:
            if s.name == name:
                return s
        raise RuntimeError("subject not found")

    def add_subject(self, subject: Subject):
        self.subjects.append(subject)

    def get_total_ects(self, weighted: bool=True) -> int:
        return sum([s.ects * (s.weight if weighted else 1) for s in self.subjects])
    
    def get_ects_per_module(self, module: MODULES, weighted: bool=True):
        # for the currently fixed module
        return sum([s.ects * (s.weight if weighted else 1) for s in self.subjects if module == s.current_module])
    
    def get_grade_per_module(self, module: MODULES, round=True, weighted: bool=True):
        ects_per_module = self.get_ects_per_module(module,  weighted=weighted)

        summed_grades = sum([s.grade * s.ects * (s.weight if weighted else 1) for s in self.subjects if module == s.current_module])
        
        if ects_per_module == 0:
            return 0
        module_grade = summed_grades / ects_per_module
        if round:
            module_grade = math.floor(module_grade * 10) / 10
        return module_grade
    
    def get_final_grade(self, round=True, verbose=False):

        final_grade = 0
        module_ects = []

        worst_grade_module = MODULES.THESIS
        worst_grade = 0
        for module in MODULES:
            module_ects = self.get_ects_per_module(module)
            module_grade = self.get_grade_per_module(module)
            if module_grade > worst_grade:
                worst_grade_module = module
                worst_grade = module_grade

        cut_off = 0
        if self.get_total_ects(weighted=True) > 120 - self.get_ects_per_module(MODULES.INTERDISCIPLINARY, weighted=False):
            cut_off = self.get_total_ects(weighted=True) - (120 - self.get_ects_per_module(MODULES.INTERDISCIPLINARY, weighted=False))
            if verbose:
                print(f"cut off {cut_off} ects from {worst_grade_module}")
        
        for module in MODULES:
            module_ects = self.get_ects_per_module(module)
            module_grade = self.get_grade_per_module(module)

            if module == worst_grade_module:
                module_ects -= cut_off
            final_grade += module_grade  * module_ects
        
        final_grade = final_grade / min(self.get_total_ects(weighted=True), 120)
        if round:
            final_grade = math.floor(final_grade * 10) / 10
        return final_grade
    

    def check_seminar_and_practicals(self, min_seminar=3, min_practical=6, min_total=12, max_total=18, weighted=True):
        sum_seminar = sum([s.ects * (s.weight if weighted else 1) for s in self.subjects if s.subject_type == SubjectType.SEMINAR and s.current_module not in [MODULES.INTERDISCIPLINARY, MODULES.MINOR]])
        sum_practical = sum([s.ects * (s.weight if weighted else 1) for s in self.subjects if s.subject_type == SubjectType.PRACTICAL and s.current_module not in [MODULES.INTERDISCIPLINARY, MODULES.MINOR]])
        
        if sum_seminar < min_seminar:
            warnings.warn("not enough ects in seminars")
        
        if sum_practical < min_practical:
            warnings.warn("not enough ects in practicals")

        if sum_seminar + sum_practical < min_total:
            warnings.warn("not enough ects combined in seminar and practical")

        if sum_seminar + sum_practical > max_total:
            warnings.warn("to many ects combined in seminar and practical")

        return sum_seminar >= min_seminar and sum_practical >= min_practical and min_total <= sum_seminar + sum_practical <= max_total

    def check_lectures(self, elective_range=(6, 49), interdisciplinary_range=(2, 6), minor_range=(9, 15), specialization_range=(15, 58), specializaiton_lecture_range=(10, 58)):
        #check elective
        sum_elective = sum([s.ects for s in self.subjects if s.current_module == MODULES.ELECTIVE])
        #check interdisciplinary
        sum_interdisciplinary = sum([s.ects for s in self.subjects if s.current_module == MODULES.INTERDISCIPLINARY])
        #check minor
        sum_minor = sum([s.ects for s in self.subjects if s.current_module == MODULES.MINOR])
        #check others
        sum_first_specialization_total = sum([s.ects for s in self.subjects if s.current_module == self.first_specialization])
        sum_first_specialization_lecture = sum([s.ects for s in self.subjects if s.current_module == self.first_specialization and s.subject_type == SubjectType.LECTURE])

        sum_second_specializaiton_total = sum([s.ects for s in self.subjects if s.current_module == self.second_specialization])
        sum_second_specializaiton_lecture = sum([s.ects for s in self.subjects if s.current_module == self.second_specialization and s.subject_type == SubjectType.LECTURE])

        return \
            elective_range[0] <= sum_elective <= elective_range[1] and \
            interdisciplinary_range[0] <= sum_interdisciplinary <= interdisciplinary_range[1] and \
            minor_range[0] <= sum_minor <= minor_range[1] and \
            specialization_range[0] <= sum_first_specialization_total <= specialization_range[1] and \
            specialization_range[0] <= sum_second_specializaiton_total <= specialization_range[1] and \
            specializaiton_lecture_range[0] <= sum_first_specialization_lecture <= specializaiton_lecture_range[1] and \
            specializaiton_lecture_range[0] <= sum_second_specializaiton_lecture <= specializaiton_lecture_range[1]
    
    def check_all(self):
        return self.check_lectures() and self.check_seminar_and_practicals() and self.get_total_ects(weighted=False) >= 120
    
    def optimize_exhaustive(self, list_of_adjustable_subjects):
        all_combinations = set(itertools.product(*[s.possible_modules for s in list_of_adjustable_subjects]))
        print("number of combinations: ", len(all_combinations))

        min_grade = 5
        optimal_assignments = {}
        for current_combination in all_combinations:
            for i, s in enumerate(list_of_adjustable_subjects):
                s.current_module = current_combination[i]
            new_min_grade = my_grade_table.get_final_grade(round=False)
            if new_min_grade < min_grade:
                min_grade = new_min_grade
                optimal_assignments[new_min_grade] = [(s.name, s.current_module) for s in choosable]
        return min_grade, optimal_assignments


    def optimize_random(self, list_of_adjustable_subjects, num_iterations=1000):
        samples_of_k_size = random.sample(list_of_adjustable_subjects, len(list_of_adjustable_subjects))

        min_grade = 5
        optimal_assignments = {}
        for i in range(num_iterations):
            for s in samples_of_k_size:
                s.current_module = s.possible_modules[random.randint(0, len(s.possible_modules)-1)]

            if my_grade_table.check_all():
                new_min_grade = my_grade_table.get_final_grade(round=False)
                if new_min_grade < min_grade:
                    min_grade = new_min_grade
                    optimal_assignments[new_min_grade] = [(s.name, s.current_module) for s in choosable]

        return min_grade, optimal_assignments


my_grade_table = GradeTable(MODULES.AI, MODULES.THEORETICAL)

# theoretical cs
my_grade_table.add_subject(Subject("FormSys", 1.7, 5, SubjectType.LECTURE, [MODULES.THEORETICAL]))
my_grade_table.add_subject(Subject("Musterekennung", 2.3, 6, SubjectType.LECTURE, [MODULES.THEORETICAL, MODULES.AI]))

# AI
my_grade_table.add_subject(Subject("NLP", 3, 6, SubjectType.LECTURE, [MODULES.AI]))
my_grade_table.add_subject(Subject("MMLLM_seminar", 1.7, 3, SubjectType.SEMINAR, [MODULES.AI]))
my_grade_table.add_subject(Subject("XAI_Prak", 2.3, 6, SubjectType.PRACTICAL, [MODULES.AI]))
my_grade_table.add_subject(Subject("MMI_seminar", 3, 3, SubjectType.SEMINAR, [MODULES.AI]))
my_grade_table.add_subject(Subject("XAI", 1.7, 3, SubjectType.LECTURE, [MODULES.AI]))
my_grade_table.add_subject(Subject("CompVision", 2.3, 3, SubjectType.LECTURE, [MODULES.AI]))
my_grade_table.add_subject(Subject("GZNS", 3, 3, SubjectType.LECTURE, [MODULES.AI]))

# elective (every subject is automatically considered part of the elective module)
my_grade_table.add_subject(Subject("CompGrafik", 1.7, 6, SubjectType.LECTURE))
my_grade_table.add_subject(Subject("QuantComp", 2.3, 2, SubjectType.LECTURE))
my_grade_table.add_subject(Subject("IT-Sicherhiet", 3, 6, SubjectType.LECTURE))
my_grade_table.add_subject(Subject("GPC-GPU", 1.7, 3, SubjectType.PRACTICAL))
my_grade_table.add_subject(Subject("Robotik", 2.3, 6, SubjectType.LECTURE))

# minor
my_grade_table.add_subject(Subject("bio_insp_robotics_prak", 3, 6, SubjectType.OTHER, [MODULES.MINOR]))
my_grade_table .add_subject(Subject("bio_insp_robotics_seminar", 1.7, 3, SubjectType.OTHER, [MODULES.MINOR]))

# interdisciplinary
my_grade_table.add_subject(Subject("language_1", 2.3, 2, SubjectType.OTHER, [MODULES.INTERDISCIPLINARY]))
my_grade_table.add_subject(Subject("language_2", 3, 2, SubjectType.OTHER, [MODULES.INTERDISCIPLINARY]))
my_grade_table.add_subject(Subject("language_3", 1.7, 2, SubjectType.OTHER, [MODULES.INTERDISCIPLINARY]))


# still waiting for grading
my_grade_table.add_subject(Subject("master_arbeit", 2.3, 30, SubjectType.OTHER, [MODULES.THESIS], weight=1)) 
my_grade_table.add_subject(Subject("CompGeom", 3, 6, SubjectType.LECTURE, [MODULES.THEORETICAL], weight=1))
my_grade_table.add_subject(Subject("QML", 1.7, 3, SubjectType.LECTURE, [MODULES.AI], weight=1))
my_grade_table.add_subject(Subject("SWT2", 2.3, 6, SubjectType.LECTURE, weight=1))



# basic information
print("all checks passed:", my_grade_table.check_all())
print("total ects: ", my_grade_table.get_total_ects(weighted=False))
print("final grade (non-optimized): ", my_grade_table.get_final_grade(round=False, verbose=True))

for m in MODULES:
    if my_grade_table.get_ects_per_module(m) > 0:
        print(m, "\n ects:", my_grade_table.get_ects_per_module(m, weighted=False), "grade:", my_grade_table.get_grade_per_module(m, weighted=False))

# pick subjects you want to possibly re-asign to a new module, the code checks itself if the asignment is possible/ valid
qml = my_grade_table.get_subject_by_name("QML")
text_mining = my_grade_table.get_subject_by_name("NLP")
mmllm = my_grade_table.get_subject_by_name("MMLLM_seminar")
xai_practical = my_grade_table.get_subject_by_name("XAI_Prak")
mmi = my_grade_table.get_subject_by_name("MMI_seminar")
xai = my_grade_table.get_subject_by_name("XAI")
comp_vision = my_grade_table.get_subject_by_name("CompVision")
gzns = my_grade_table.get_subject_by_name("GZNS")

choosable = [qml, text_mining, mmllm, xai_practical, mmi, xai, comp_vision, gzns]


# find best grade by exhaustive search (for large number of choosable subjects, this can take long)
print()
min_grade, optimal_assignments = my_grade_table.optimize_exhaustive(choosable)
print("minimum grade found (exhaustive): ", min_grade)
print("optimal assignments:")
for grade_key in optimal_assignments:
    print("for grade: ", grade_key)
    for subject in optimal_assignments[grade_key]:
        print(" ", subject[0], subject[1])
    print()
    


# random search for best re-asignment
"""
min_grade, optimal_assignment = my_grade_table.optimize_random(choosable, num_iterations=1000) 
print("minimum grade found (random): ", min_grade)
print("optimal assignments:")
for grade_key in optimal_assignments:
    print("for grade: ", grade_key)
    for subject in optimal_assignments[grade_key]:
        print(" ", subject[0], subject[1])
    print()
"""