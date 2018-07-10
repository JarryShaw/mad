import glob
from .fingerprint import FingerprintManager

class DetectionModule():
    """
    This class is responsible to compare fingerprints and identify potentially malicious requests.
    """
    
    def __init__(self):
        self.background_threshold = 2.0
        self.browser_threshold = 1.5
        
        

    def similarity_check(self, new_f1, old_f2):
        """
            Verify if two fingerprints are similar
            
            Parameter
            -----------
            new_f1, old_f2 : Fingerprint

                
            Result:
            -----------
            True : if new_f1 and old_f2 are similar
            False: otherwise
        """
        score = 0.0
        
        if not new_f1 or not old_f2:
            return False
 
        # Fingerprints are not similar if they represents two different type of application
        if new_f1.label != old_f2.label:
            return False
        
        # Check if Background-type fingerprints are similar
        if new_f1.label == "Background":
            score = self._background_similarity(new_f1, old_f2)
            if score >= self.background_threshold:
                return True
            else:
                return False
        
        # Check if Browser-type fingerprints are similar
        else:
            score = self._browser_similarity(new_f1, old_f2)
            if score >= self.browser_threshold:
                return True
            else:
                return False
    
    
    def _background_similarity(self, new_f1, old_f2):
        """
        This method computes the similarity between two Background-type fingerprints based on their core features.

            Parameters
            --------------
            new_f1 : (Background) Fingerprint
            old_f2 : (Background) Fingerprint

            Returns
            --------------
            score : float
                The similarity score between two Background-type fingerprints
        """
        score = 0.0
        score += self._ip_check(new_f1.ip_dsts, old_f2.ip_dsts)
        score += self._avg_size_check(new_f1.avg_size, old_f2.avg_size)
        score += self._header_check(new_f1.constant_header_fields, old_f2.constant_header_fields)
        score += self._ua_check(new_f1.user_agent, old_f2.user_agent)
        return score
    
    
    def _browser_similarity(self, new_f1, old_f2):
        """
        This method computes the similarity between two Browser-type fingerprints based on their core features.

            Parameters
            --------------
            new_f1 : (Browser) Fingerprint
            old_f2 : (Browser) Fingerprint

            Returns
            --------------
            score : float
                The similarity score between two Browser-type fingerprints
        """
        score = 0.0
        score += self._ua_check(new_f1.user_agent, old_f2.user_agent)
        score += self._language_check(new_f1.language, old_f2.language)
        score += self._ip_check(new_f1.ip_dsts, old_f2.ip_dsts)
        return score
    
    
    def _ip_check(self, new_ip, old_ip):
        """
        This method checks if the set of hosts of the old fingerprint is a superset of the new fingerprint's list of hosts.

            Parameters
            --------------
            new_host_list: list of string
            old_host2_list : list of string

            Returns
            -------------
            result : float
                The result of this similarity function between the HTTP host features.
        """
        result = 0.0
        if new_ip == old_ip:
            result += 1.0
            return result
        else:
            return result
    
    
    def _avg_size_check(self, new_avg, old_avg):
        """
        This method checks if the average request size of the new fingerprint falls within a certain range 
        from the average size of the old fingerprint.

            Parameters
            --------------
            new_avg: int
            old_avg: int

            Returns
            --------------
            result : float
                The result of this similaritfy function based on the average size of HTTP requests
        """
        avg_percentage_error = 30
        result = 0.0
        error_margin = (float(old_avg)/ 100) * avg_percentage_error
        
        if (float(old_avg) + error_margin) >= float(new_avg) >= (float(old_avg) - error_margin):
            result = 1.0
            return result
        elif (float(old_avg) + 2 * error_margin) >= float(new_avg) >= (float(old_avg) - 2 * error_margin):
            result = 0.5
            return result
        else:
            return result
        
        
    def _header_check(self, new_const_headers, old_const_headers):
        """
        This method checks if the set of constant headers of the new fingerprint fully or partially match with the
        list of constant headers of the old fingerprint.

            Parameters
            ---------------
            new_const_headers: list of string
            old_const_headers: list of string

            Returns
            ---------------
            result: float
                The result of this similarity function based on the constant headers present in HTTP requests.
        """
        matches = 0
        result = 0.0
        for header in new_const_headers:
            if header in old_const_headers:
                matches += 1
        if matches == len(old_const_headers) and len(new_const_headers) == len(old_const_headers):
            result += 0.5
            return result
        elif matches == len(old_const_headers) and len(new_const_headers) > len(old_const_headers):
            result += 0.5
            return result
        else:
            return result
        
    
    def _ua_check(self, new_ua, old_ua):
        """
        This methods verifies that two User-Agents are matching.

            Parameters
            -------------
            new_ua: string
            old_ua: string

            Returns
            -------------
            result: float
                Returns 1.0 if there is a match, 0.0 otherwise.
        """
        result = 0.0
        if new_ua == old_ua:
            result += 1.0
            return result
        else:
            return result
        
    
    def _language_check(self, new_lang, old_lang):
        """
        This methods verifies that two Accept-Language values are matching. (Same check as _ua_check() )

            Parameters
            -------------
            new_lang: string
            old_lang: string

            Returns
            -------------
            result: float
                Returns 1.0 if there is a match, 0.0 otherwise.
        """
        result = 0.0
        if new_lang == old_lang:
            result += 0.5
            return result
        else:
            return result



