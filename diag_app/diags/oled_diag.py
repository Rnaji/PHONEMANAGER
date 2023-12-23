class OledDiagnostic:
    GRADE_A = "GRADE A"
    GRADE_B = "GRADE B"
    GRADE_C = "GRADE C"
    GRADE_D = "GRADE D"
    GRADE_E = "GRADE E"
    GRADE_F = "GRADE F"
    GRADE_G = "GRADE G"
    GRADE_AFTERMARKET = "GRADE AFTERMARKET"
    GRADE_POUBELLE = "GRADE POUBELLE"
    GRADE_HS = "GRADE HS"

    def __init__(self):
        self.grade = None  # Ajout d'un attribut pour stocker le résultat de grade

    def run_diagnostic(self):
        print("Commencer le diagnostic...")
        self.grade = self.grade_diagnostic()
        print("Résultat du diagnostic :", self.grade)

    def grade_diagnostic(self):
        question1 = input("(1) L’écran est original (oui/non) ?")
        question2 = input("(2) " + self.get_question_text(2))
        question3 = input("(3) " + self.get_question_text(3))
        question4 = input("(4) " + self.get_question_text(4))

        if question4.lower() == "non":
            question5 = "non"  # Sauter la question 5 si la réponse à la question 4 est "non"
        else:
            question5 = input("(5) " + self.get_question_text(5))

        question6 = input("(6) " + self.get_question_text(6))
        if question6.lower() == "non":
            question7 = "non"  # Sauter la question 7 si la réponse à la question 6 est "non"
            question8 = "non"  # Sauter la question 8 si la réponse à la question 6 est "non"
        else:
            question7 = input("(7) " + self.get_question_text(7))
            question8 = input("(8) " + self.get_question_text(8))

        if (
            question1.lower() == "oui" and
            question2.lower() == "non" and
            question3.lower() == "non" and
            question4.lower() == "non" and
            question6.lower() == "non"
        ):
            return self.GRADE_A

        if (
            question1.lower() == "non" and
            question2.lower() == "non" and
            question3.lower() == "non" and
            question4.lower() == "non" and
            question6.lower() == "non"
        ):
            return self.GRADE_AFTERMARKET

        if (
            question1.lower() == "oui" and
            question2.lower() == "oui" and
            question3.lower() == "non" and
            question4.lower() == "non" and
            question6.lower() == "non"
        ):
            return self.GRADE_G

        if (
            question1.lower() == "oui" and
            question2.lower() == "non" and
            question3.lower() == "non" and
            question4.lower() == "oui" and
            question5.lower() == "non" and
            question6.lower() == "non"
        ):
            return self.GRADE_E

        if (
            question1.lower() == "oui" and
            question2.lower() == "non" and
            question3.lower() == "non" and
            question4.lower() == "oui" and
            question5.lower() == "oui" and
            question6.lower() == "non"
        ):
            return self.GRADE_F

        if (
            question1.lower() == "oui" and
            question2.lower() == "non" and
            question3.lower() == "non" and
            question4.lower() == "non" and
            question6.lower() == "oui" and
            question7.lower() == "non" and
            question8.lower() == "non"
        ):
            return self.GRADE_C

        if (
            question1.lower() == "oui" and
            question2.lower() == "non" and
            question3.lower() == "non" and
            question4.lower() == "non" and
            question6.lower() == "oui" and
            question7.lower() == "non" and
            question8.lower() == "oui"
        ):
            return self.GRADE_D

        if (
            question1.lower() == "oui" and
            question2.lower() == "non" and
            question3.lower() == "non" and
            question4.lower() == "non" and
            question6.lower() == "oui" and
            question7.lower() == "oui"
        ):
            return self.GRADE_B

        return self.GRADE_HS

    def get_question_text(self, question_number):
        questions = {
            1: "L’écran est original (oui/non) ?",
            2: "Le tactile est défectueux (oui/non) ?",
            3: "L’écran présente des dommages fonctionnels (oui/non) ?",
            4: "L’écran a des points noirs (oui/non) ?",
            5: "Ces points noirs sont gros (oui/non) ?",
            6: "L’écran a des ombres persistantes (oui/non) ?",
            7: "Ces ombres sont presque invisibles (oui/non) ?",
            8: "Ces ombres sont très visibles (oui/non) ?"
        }
        return questions[question_number]

    def get_questions(self):
        return [
            {"qid": 1, "text": self.get_question_text(1)},
            {"qid": 2, "text": self.get_question_text(2)},
            {"qid": 3, "text": self.get_question_text(3)},
            {"qid": 4, "text": self.get_question_text(4)},
            {"qid": 5, "text": self.get_question_text(5)},
            {"qid": 6, "text": self.get_question_text(6)},
            {"qid": 7, "text": self.get_question_text(7)},
            {"qid": 8, "text": self.get_question_text(8)},
        ]

if __name__ == "__main__":
    diagnostic = OledDiagnostic()
    diagnostic.run_diagnostic()
