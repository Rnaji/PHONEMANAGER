class NonOledDiagnostic:
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
        self.grade = None

    def run_diagnostic(self):
        print("Commencer le diagnostic...")
        self.grade = self.grade_diagnostic()
        print("Résultat du diagnostic :", self.grade)

    def grade_diagnostic(self):
        question1 = input("(1) L’écran est original (oui/non) ?").lower()
        question2 = input("(2) " + self.get_question_text(2)).lower()
        question3 = input("(3) " + self.get_question_text(3)).lower()
        question4 = input("(4) " + self.get_question_text(4)).lower()
        question5 = input("(5) " + self.get_question_text(5)).lower()
        question6 = input("(6) " + self.get_question_text(6)).lower()
        question7 = input("(7) " + self.get_question_text(7)).lower()
        question8 = input("(8) " + self.get_question_text(8)).lower()

        if question8 == "non":
            question9 = "non"
        else:
            question9 = input("(9) " + self.get_question_text(9)).lower()

        if (
            question1 == "oui" and
            question2 == "non" and
            question3 == "non" and
            question4 == "non" and
            question5 == "non" and
            question6 == "non" and
            question7 == "non" and
            question8 == "non" and
            question9 == "non"
        ):
            return self.GRADE_A

        if (
            question1 == "non" and
            question2 == "non" and
            question3 == "non" and
            question4 == "non" and
            question5 == "non" and
            question6 == "non" and
            question7 == "non" and
            question8 == "non" and
            question9 == "non"
        ):
            return self.GRADE_AFTERMARKET

        if (
            question1 == "oui" and
            question2 == "non" and
            question3 == "oui" and
            question4 == "non" and
            question5 == "non" and
            question6 == "non" and
            question7 == "non" and
            question8 == "non" and
            question9 == "non"
        ):
            return self.GRADE_B

        if (
            question1 == "oui" and
            question2 == "non" and
            question3 == "non" and
            question4 == "oui" and
            question5 == "non" and
            question6 == "non" and
            question7 == "non" and
            question8 == "non" and
            question9 == "non"
        ):
            return self.GRADE_B

        if (
            question1 == "oui" and
            question2 == "non" and
            question3 == "non" and
            question4 == "non" and
            question5 == "oui" and
            question6 == "non" and
            question7 == "non" and
            question8 == "non" and
            question9 == "non"
        ):
            return self.GRADE_G

        if (
            question1 == "oui" and
            question2 == "non" and
            question3 == "non" and
            question4 == "non" and
            question5 == "non" and
            question6 == "oui" and
            question7 == "non" and
            question8 == "non" and
            question9 == "non"
        ):
            return self.GRADE_D

        if (
            question1 == "oui" and
            question2 == "non" and
            question3 == "non" and
            question4 == "non" and
            question5 == "non" and
            question6 == "non" and
            question7 == "oui" and
            question8 == "non" and
            question9 == "non"
        ):
            return self.GRADE_B

        if (
            question1 == "non" or
            question2 == "oui" or
            question3 == "oui" or
            question4 == "oui" or
            question5 == "oui" or
            question6 == "oui" and
            question7 == "oui" and
            question8 == "oui" and
            question9 == "oui"
        ):
            return self.GRADE_POUBELLE

        if (
            question1 == "oui" and
            question2 == "non" and
            question3 == "non" and
            question4 == "non" and
            question5 == "non" and
            question6 == "non" and
            question7 == "oui" and
            question8 == "oui" and
            question9 == "non"
        ):
            return self.GRADE_C

        return self.GRADE_HS

    def get_user_answers(self):
        answers = []
        for i in range(1, 9):
            answer = input(f"({i}) {self.get_question_text(i)} ").lower()
            answers.append(answer)
        return answers

    def get_question_text(self, question_number):
        questions = {
            1: "L’écran est original (oui/non) ?",
            2: "L’écran présente des dommages fonctionnels (oui/non) ?",
            3: "L’écran a des problèmes de rétroéclairage (oui/non) ?",
            4: "L’écran est jaunâtre (oui/non) ?",
            5: "Le tactile est défectueux (oui/non) ?",
            6: "Le 3D Touch est défectueux (oui/non) ?",
            7: "L’écran a des points lumineux ou une distorsion des couleurs (oui/non) ?",
            8: "L’écran a des pixels morts (oui/non) ?",
            9: "L’écran a des Gros pixels morts (oui/non) ?"
        }
        return questions[question_number]

if __name__ == "__main__":
    diagnostic = NonOledDiagnostic()
    diagnostic.run_diagnostic()
