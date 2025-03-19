"""
Settings module voor Excelladin Reloaded
Beheert applicatie-instellingen zoals laatst geopende bestanden
"""
import os
import configparser
from modules.logger import logger

def maak_relatief_pad(pad):
    """
    Converteer een absoluut pad naar een relatief pad t.o.v. de huidige werkdirectory
    
    Args:
        pad (str): Het absolute pad dat geconverteerd moet worden
        
    Returns:
        str: Het relatieve pad, of het originele pad als het al relatief is
    """
    try:
        # Als het pad al relatief is, geef het terug zoals het is
        if not os.path.isabs(pad):
            return pad
        
        # Converteer naar relatief pad t.o.v. huidige werkdirectory
        werkdir = os.getcwd()
        rel_pad = os.path.relpath(pad, werkdir)
        logger.logInfo(f"Pad geconverteerd naar relatief: {rel_pad}")
        return rel_pad
    except Exception as e:
        logger.logFout(f"Fout bij converteren naar relatief pad: {e}")
        return pad  # Bij fouten, geef het originele pad terug

def maak_absoluut_pad(pad):
    """
    Converteer een relatief pad naar een absoluut pad
    
    Args:
        pad (str): Het relatieve pad dat geconverteerd moet worden
        
    Returns:
        str: Het absolute pad, of het originele pad als het al absoluut is
    """
    try:
        # Als het pad al absoluut is, geef het terug zoals het is
        if os.path.isabs(pad):
            return pad
        
        # Converteer naar absoluut pad
        abs_pad = os.path.abspath(pad)
        logger.logInfo(f"Pad geconverteerd naar absoluut: {abs_pad}")
        return abs_pad
    except Exception as e:
        logger.logFout(f"Fout bij converteren naar absoluut pad: {e}")
        return pad  # Bij fouten, geef het originele pad terug

def zorg_voor_directory(directory_pad):
    """
    Zorgt ervoor dat de opgegeven directory bestaat, maakt deze aan indien nodig
    
    Args:
        directory_pad (str): Pad naar de directory die moet bestaan
        
    Returns:
        bool: True als de directory bestaat of succesvol is aangemaakt, anders False
    """
    try:
        # Converteer naar absoluut pad voor consistentie
        abs_dir = maak_absoluut_pad(directory_pad)
        
        # Controleer of de directory bestaat, zo niet maak deze aan
        if not os.path.exists(abs_dir):
            os.makedirs(abs_dir)
            logger.logInfo(f"Directory aangemaakt: {abs_dir}")
        return True
    except Exception as e:
        logger.logFout(f"Fout bij aanmaken directory {directory_pad}: {e}")
        return False

class Instellingen:
    """Instellingen klasse voor het beheren van applicatie-instellingen"""
    
    def __init__(self, configBestand="config.ini"):
        """
        Initialiseer de instellingen
        
        Args:
            configBestand (str): Pad naar het configuratiebestand
        """
        self.configBestand = configBestand
        self.config = configparser.ConfigParser()
        
        # Standaardinstellingen
        self.standaardInstellingen = {
            'Algemeen': {
                'LaatsteBestand': '',
                'OnthoudBestand': 'False',
            },
            'Interface': {
                'ToonTooltips': 'True',
            }
        }
        
        # Laad bestaande instellingen of maak nieuwe
        if os.path.exists(self.configBestand):
            try:
                self.config.read(self.configBestand, encoding='utf-8')
                logger.logInfo("Instellingen geladen uit bestand")
            except Exception as e:
                logger.logFout(f"Fout bij laden instellingen: {e}")
                self._maakStandaardInstellingen()
        else:
            self._maakStandaardInstellingen()
    
    def _maakStandaardInstellingen(self):
        """Maak standaardinstellingen aan"""
        for sectie, opties in self.standaardInstellingen.items():
            if not self.config.has_section(sectie):
                self.config.add_section(sectie)
            
            for optie, waarde in opties.items():
                self.config.set(sectie, optie, waarde)
        
        self.slaOp()
        logger.logInfo("Standaardinstellingen aangemaakt")
    
    def haalOp(self, sectie, optie, standaard=None):
        """
        Haal een instelling op
        
        Args:
            sectie (str): Configuratie sectie
            optie (str): Optienaam
            standaard: Standaardwaarde als de optie niet bestaat
            
        Returns:
            Waarde van de optie of standaardwaarde
        """
        try:
            # Converteer sectie en optie naar lowercase voor hoofdletterongevoelige vergelijking
            sectie_lower = sectie.lower()
            optie_lower = optie.lower()
            
            # Zoek door alle secties en opties op een hoofdletterongevoelige manier
            for config_sectie in self.config.sections():
                if config_sectie.lower() == sectie_lower:
                    for config_optie in self.config.options(config_sectie):
                        if config_optie.lower() == optie_lower:
                            return self.config.get(config_sectie, config_optie)
            
            return standaard
        except Exception as e:
            logger.logFout(f"Fout bij ophalen instelling {sectie}.{optie}: {e}")
            return standaard
    
    def stelIn(self, sectie, optie, waarde):
        """
        Stel een instelling in
        
        Args:
            sectie (str): Configuratie sectie
            optie (str): Optienaam
            waarde: Nieuwe waarde voor de optie
        """
        try:
            # Converteer sectie en optie naar lowercase voor hoofdletterongevoelige vergelijking
            sectie_lower = sectie.lower()
            optie_lower = optie.lower()
            
            # Zoek of er al een sectie bestaat met dezelfde naam (hoofdletterongevoelig)
            bestaande_sectie = None
            for config_sectie in self.config.sections():
                if config_sectie.lower() == sectie_lower:
                    bestaande_sectie = config_sectie
                    break
            
            # Als er geen sectie bestaat, maak een nieuwe aan met de originele hoofdletters
            if bestaande_sectie is None:
                self.config.add_section(sectie)
                bestaande_sectie = sectie
            
            # Zoek of er al een optie bestaat met dezelfde naam (hoofdletterongevoelig)
            bestaande_optie = None
            for config_optie in self.config.options(bestaande_sectie):
                if config_optie.lower() == optie_lower:
                    bestaande_optie = config_optie
                    break
            
            # Gebruik de bestaande optie naam of de originele als er geen bestaat
            te_gebruiken_optie = bestaande_optie if bestaande_optie else optie
            
            # Stel de waarde in
            self.config.set(bestaande_sectie, te_gebruiken_optie, str(waarde))
            self.slaOp()
            logger.logInfo(f"Instelling {bestaande_sectie}.{te_gebruiken_optie} ingesteld op {waarde}")
        except Exception as e:
            logger.logFout(f"Fout bij instellen {sectie}.{optie}: {e}")
    
    def slaOp(self):
        """Sla instellingen op naar bestand"""
        try:
            with open(self.configBestand, 'w', encoding='utf-8') as bestand:
                self.config.write(bestand)
        except Exception as e:
            logger.logFout(f"Kon instellingen niet opslaan: {e}")
    
    def haalLaatsteBestand(self):
        """
        Haal het laatst gebruikte bestand op
        
        Returns:
            str: Pad naar laatst gebruikte bestand of leeg als er geen is
        """
        onthoud = self.haalOp('Algemeen', 'OnthoudBestand') == 'True'
        if onthoud:
            return self.haalOp('Algemeen', 'LaatsteBestand', '')
        return ''
    
    def stelLaatsteBestandIn(self, bestandspad):
        """
        Sla het laatst gebruikte bestand op
        
        Args:
            bestandspad (str): Pad naar het bestand
        """
        # Sla relatief pad op voor betere portabiliteit
        rel_pad = maak_relatief_pad(bestandspad)
        self.stelIn('Algemeen', 'LaatsteBestand', rel_pad)
    
    def stelOnthoudBestandIn(self, onthoud):
        """
        Stel in of het laatst gebruikte bestand moet worden onthouden
        
        Args:
            onthoud (bool): True als het bestand moet worden onthouden
        """
        self.stelIn('Algemeen', 'OnthoudBestand', str(onthoud))
    
    def haalAbsoluutPad(self, sectie, optie, standaard=None):
        """
        Haal een pad-instelling op en converteer naar absoluut pad
        
        Args:
            sectie (str): Configuratie sectie
            optie (str): Optienaam
            standaard: Standaardwaarde als de optie niet bestaat
            
        Returns:
            str: Absoluut pad naar het bestand of standaardwaarde
        """
        pad = self.haalOp(sectie, optie, standaard)
        if pad:
            return maak_absoluut_pad(pad)
        return standaard

# Singleton instance voor gebruik in de hele applicatie
instellingen = Instellingen()
